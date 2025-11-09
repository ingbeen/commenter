from api.generate_comment import (
    truncate_text_to_token_limit,
    is_token_length_valid,
)
from driver.driver_manager import DriverManager
from naver.comment_writer import CommentWriter
from naver.comment_scraper import CommentScraper
from naver.buddy_scraper import BuddyScraper
from naver.blog_scraper import BlogScraper
from common.log_utils import error_log, logger
from common.human_behavior import (
    simulate_reading,
    BOT_EVASION_ENABLED,
    TOTAL_STAY_DURATION_MIN,
    TOTAL_STAY_DURATION_MAX,
)
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)
import openai
import sys
import random


class CommentProcessor:
    """
    네이버 블로그 자동 댓글 작성 프로세스를 관리하는 핵심 클래스

    최근 댓글 작성자 및 서로이웃의 블로그를 순회하며 자동으로 댓글을 작성합니다.
    블로그 크롤링, 댓글 생성(OpenAI API), 댓글 작성의 전체 프로세스를 조율하며
    예외 상황(Alert, API Rate Limit 등)을 처리합니다.

    Attributes:
        driver_manager (DriverManager): WebDriver 관리 객체
        repeat_count (int): 총 시도한 블로그 수
        success_count (int): 댓글 작성에 성공한 블로그 수
        alert_count (int): 발생한 Alert 예외 횟수
    """

    ALERT_THRESHOLD = 5

    def __init__(self, driver_manager: DriverManager):
        """
        CommentProcessor 초기화

        Args:
            driver_manager: Selenium WebDriver를 관리하는 DriverManager 인스턴스
        """
        self.driver_manager = driver_manager
        self.repeat_count = 0
        self.success_count = 0
        self.alert_count = 0

    def _process_single_blog(self, blog_id, blog_scraper):
        """
        단일 블로그에 대해 댓글 작성 프로세스를 실행

        블로그 크롤링 → 토큰 검증 → 공감 버튼 클릭 → 댓글 생성 → 댓글 작성의
        전체 플로우를 수행하고, 발생 가능한 예외를 처리합니다.

        Args:
            blog_id (str): 대상 블로그 ID
            blog_scraper (BlogScraper): 블로그 크롤링 객체
        """
        self.repeat_count += 1

        try:
            # 1. 블로그 페이지 이동 및 게시글 크롤링
            url = blog_scraper.go_to_blog(blog_id)
            header = blog_scraper.get_post_header()
            content = blog_scraper.get_post_content()

            # 2. 본문 토큰 수 제한
            content = truncate_text_to_token_limit(content)

            # 3. 최소 토큰 수 검증
            if not is_token_length_valid(content):
                logger.info("본문 글자수 적음")
                return

            # 4. 공감 버튼 클릭 시도
            comment_writer = CommentWriter(self.driver_manager)
            comment_writer.press_like_if_needed()

            # 5. 댓글 관련 요소 초기화 및 댓글 수 확인
            comment_writer.init_comment_button()
            comment_writer.set_can_add_comment()

            # 6. 댓글 작성 가능 여부 검증
            # - 공감 버튼을 클릭했는지 확인
            # - 댓글 수가 제한 이하인지 확인
            if (
                not comment_writer.did_press_like
                or not comment_writer.is_under_comment_limit
            ):
                logger.info("댓글 등록 제외")
                return

            # 7. 봇 탐지 회피: 페이지 읽기 시뮬레이션 (20-30초 체류)
            if BOT_EVASION_ENABLED:
                target_duration = random.uniform(
                    TOTAL_STAY_DURATION_MIN, TOTAL_STAY_DURATION_MAX
                )
                simulate_reading(
                    self.driver_manager.get_driver(),
                    target_duration,
                    comment_writer.btn_comment,
                )

            # 8. 댓글 작성 및 성공 여부 확인
            # (댓글 입력창 확인 후 OpenAI API 호출하여 댓글 생성 및 작성)
            is_success = comment_writer.add_comment(header, content)
            if is_success:
                self.success_count += 1
        except openai.RateLimitError as e:
            # OpenAI API Rate Limit 초과 시 즉시 프로그램 중단
            # (API 요금 한도 초과 또는 요청 제한 도달)
            error_log(e, url)
            logger.error("[자동화 중단] OpenAI API Rate Limit 초과")
            self.driver_manager.quit()
            sys.exit("[자동화 중단] OpenAI API Rate Limit 초과")
        except UnexpectedAlertPresentException as e:
            # 네이버 경고창(Alert) 발생 시 처리
            try:
                alert_text = getattr(e, "alert_text", "alert_err")
                logger.error(f"alert_text : {alert_text}")
                alert = self.driver_manager.get_driver().switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass

            error_log(e, url)
            self.alert_count += 1

            logger.error(f"alert_count = {self.alert_count}")
            # Alert가 임계값 이상 발생하거나 "더이상 등록할 수 없습니다" 메시지 발생 시 중단
            if (
                "더이상 등록할 수 없습니다" in alert_text
                or self.alert_count >= self.ALERT_THRESHOLD
            ):
                self.driver_manager.quit()
                sys.exit(f"[자동화 중단] 네이버 댓글 제한 경고창")
        except NoSuchElementException as e:
            # 자주 발생하는 요소 누락 예외는 로그만 기록하고 계속 진행
            if '[id="post_1"]' in str(e) or 'id="post_1"' in str(e):
                logger.error("예외처리 / post_1 없음")
            elif ".area_sympathy" in str(e) or 'class="area_sympathy"' in str(e):
                logger.error("예외처리 / area_sympathy 없음")
            elif ".area_comment .btn_comment" in str(e) or 'class="btn_comment"' in str(
                e
            ):
                logger.error("예외처리 / btn_comment 없음")
            else:
                error_log(e, url)
        except Exception as e:
            # 기타 모든 예외는 로그 기록 후 계속 진행
            error_log(e, url)

    def _process_loop_blog(self, commenter_ids):
        """
        여러 블로그를 순회하며 댓글 작성 프로세스를 반복 실행

        Args:
            commenter_ids (list[str]): 처리할 블로그 ID 목록
        """
        blog_scraper = BlogScraper(self.driver_manager)

        for blog_id in commenter_ids:
            self._process_single_blog(blog_id, blog_scraper)
            logger.info(
                f"repeat_count = {self.repeat_count} / success_count = {self.success_count}"
            )

    def run(self):
        """
        자동 댓글 작성 프로세스의 메인 실행 함수

        1. 최근 댓글 작성자 수집 및 처리
        2. 서로이웃 최근 게시자 수집
        3. 중복 제거 후 추가 처리
        """
        # 1. 최근 댓글 작성자 처리
        comment_scraper = CommentScraper(self.driver_manager)
        recent_commenter_ids = comment_scraper.get_recent_commenter_ids()
        self._process_loop_blog(recent_commenter_ids)

        # 2. 서로이웃 최근 게시자 수집
        buddy_scraper = BuddyScraper(self.driver_manager)
        recent_posting_buddy_ids = buddy_scraper.get_recent_posting_buddy_ids()

        # 3. 이미 댓글 작성한 블로그를 제외한 서로이웃 필터링
        recent_commenter_set = set(recent_commenter_ids)
        filtered_ids = [
            blog_id
            for blog_id in recent_posting_buddy_ids
            if blog_id not in recent_commenter_set
        ]

        self._process_loop_blog(filtered_ids)
