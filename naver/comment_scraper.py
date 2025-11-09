from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from driver.base_driver import BaseDriver
from common.constants import EXCLUDED_BLOG_IDS, MY_BLOG_ID, RECENT_COMMENTER_LIMIT
from common.log_utils import logger
from driver.driver_manager import DriverManager
import time


class CommentScraper(BaseDriver):
    def __init__(self, driver_manager: DriverManager):
        super().__init__(driver_manager)

    def get_recent_commenter_ids(self) -> list[str]:
        page = 1
        collected_ids = set()

        while len(collected_ids) < RECENT_COMMENTER_LIMIT:
            self._go_to_comment_manage(page)

            # 1. tableListById 요소 찾기 시도
            try:
                table = self.driver_manager.get_driver().find_element(
                    By.ID, "tableListById"
                )
            except NoSuchElementException:
                # 2. 현재 URL 확인하여 로그인 페이지인지 검사
                current_url = self.driver_manager.get_driver().current_url

                if "nid.naver.com/nidlogin.login" in current_url:
                    # 로그인 페이지로 리다이렉트된 경우
                    logger.warning(
                        "수동으로 로그인을 진행해주세요. 로그인 완료를 대기 중입니다..."
                    )

                    # 3. 로그인 완료 감지 (최대 5분 대기)
                    login_success = self._wait_for_login(max_wait_seconds=300)

                    if login_success:
                        logger.info("로그인이 완료되었습니다. 댓글 수집을 계속합니다.")
                        # 4. 로그인 후 다시 댓글 관리 페이지로 이동
                        self._go_to_comment_manage(page)
                        table = self.driver_manager.get_driver().find_element(
                            By.ID, "tableListById"
                        )
                    else:
                        logger.error(
                            "로그인 대기 시간이 초과되었습니다. 프로그램을 종료합니다."
                        )
                        raise Exception("로그인 실패: 시간 초과")
                else:
                    # 로그인 페이지가 아닌 다른 이유로 요소를 찾지 못한 경우
                    logger.error(
                        f"tableListById 요소를 찾을 수 없습니다. 현재 URL: {current_url}"
                    )
                    raise  # 원래 예외를 그대로 발생시켜 프로그램 종료

            blog_id_elements = table.find_elements(By.CSS_SELECTOR, "span.blogid")

            for el in blog_id_elements:
                blog_id = el.text.strip()
                if blog_id and blog_id not in EXCLUDED_BLOG_IDS:
                    collected_ids.add(blog_id)
            page += 1

        return list(collected_ids)

    def _wait_for_login(self, max_wait_seconds: int = 300) -> bool:
        """
        사용자가 수동으로 로그인을 완료할 때까지 대기합니다.

        Args:
            max_wait_seconds: 최대 대기 시간(초)

        Returns:
            로그인 성공 시 True, 시간 초과 시 False
        """
        start_time = time.time()
        check_interval = 3  # 3초마다 확인

        while time.time() - start_time < max_wait_seconds:
            try:
                current_url = self.driver_manager.get_driver().current_url

                # 1. admin.blog.naver.com 도메인으로 돌아왔는지 확인
                if "admin.blog.naver.com" in current_url:
                    # 2. content 요소가 존재하는지 확인
                    try:
                        self.driver_manager.get_driver().find_element(By.ID, "content")
                        # 3. 요소를 찾았다면 로그인 성공
                        return True
                    except NoSuchElementException:
                        # 아직 로그인 페이지에 있거나 로딩 중
                        pass

            except WebDriverException as e:
                # 브라우저 종료 또는 연결 끊김
                logger.error(f"WebDriver 연결이 끊어졌습니다: {e}")
                return False
            except Exception as e:
                logger.error(f"로그인 확인 중 예외 발생: {e}")

            time.sleep(check_interval)

        return False

    def _go_to_comment_manage(self, page):
        url = f"https://admin.blog.naver.com/AdminNaverCommentManageView.naver?paging.commentSearchType=0&paging.economyTotalCount=8220&paging.commentSearchValue=&blogId={MY_BLOG_ID}&paging.currentPage={page}"
        self.get(url)
