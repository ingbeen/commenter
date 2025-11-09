from selenium.webdriver.common.by import By
from driver.base_driver import BaseDriver
from common.time_utils import wait_random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.log_utils import logger
from common.constants import MY_BLOG_ID
from driver.driver_manager import DriverManager
from api.generate_comment import generate_comment
import random
import time


# ============================================================================
# 상수 정의
# ============================================================================

# 댓글 작성이 가능한 기존 댓글 수의 최대값
MAX_EXISTING_COMMENTS = 100


class CommentWriter(BaseDriver):
    """
    네이버 블로그 댓글 작성 및 공감 버튼 클릭을 담당하는 클래스

    공감 버튼 클릭 → 댓글 수 확인 → 댓글 작성 → 작성 검증의
    전체 댓글 작성 프로세스를 수행합니다.

    Attributes:
        did_press_like (bool): 공감 버튼 클릭 성공 여부
        is_under_comment_limit (bool): 댓글 수 제한 이하 여부
        btn_comment: 댓글 버튼 웹 요소
        post_1: 게시글 메인 웹 요소
    """

    def __init__(self, driver_manager: DriverManager):
        """
        CommentWriter 초기화

        Args:
            driver_manager: Selenium WebDriver를 관리하는 DriverManager 인스턴스
        """
        super().__init__(driver_manager)
        self.did_press_like = False
        self.is_under_comment_limit = False
        self.btn_comment = None
        self.post_1 = None

    def press_like_if_needed(self):
        """
        공감 버튼 클릭 시도 (이미 클릭되어 있으면 스킵)

        공감 버튼이 이미 'on' 상태인지 확인하고,
        클릭되지 않은 경우에만 클릭합니다.
        """
        # 1. 게시글 영역 및 공감 버튼 요소 탐색
        post_1 = self.driver_manager.get_driver().find_element(By.ID, "post_1")
        area_sympathy = post_1.find_element(By.CSS_SELECTOR, ".area_sympathy")
        u_likeit_list_module = area_sympathy.find_element(
            By.CSS_SELECTOR, ".u_likeit_list_module"
        )
        u_likeit_list_btn = u_likeit_list_module.find_element(
            By.CSS_SELECTOR, "a.u_likeit_button"
        )

        # 2. 공감 버튼이 이미 클릭된 상태인지 확인
        if "on" in u_likeit_list_btn.get_attribute("class").split():
            logger.info(f"공감 버튼 눌러져 있음")
            return

        # 3. 공감 버튼 클릭
        u_likeit_list_btn.click()
        logger.info(f"공감 버튼 클릭")
        self.did_press_like = True

        # 4. 랜덤 대기
        wait_random()

    def init_comment_button(self):
        """
        댓글 버튼 요소를 찾아서 초기화
        """
        post_1 = self.driver_manager.get_driver().find_element(By.ID, "post_1")
        self.btn_comment = post_1.find_element(
            By.CSS_SELECTOR, ".area_comment .btn_comment"
        )

    def set_can_add_comment(self):
        """
        현재 게시글의 댓글 수를 확인하고 댓글 작성 가능 여부를 설정

        댓글 수가 제한 이하인 경우에만 댓글 작성이 가능합니다.
        """
        # 댓글 수 텍스트 추출
        comment_text = self.btn_comment.find_element(
            By.CSS_SELECTOR, "#commentCount"
        ).text.strip()

        # 정수 변환 (실패 시 0으로 처리)
        try:
            comment_count_int = int(comment_text)
        except ValueError:
            comment_count_int = 0

        logger.info(f"현재 포스팅글 댓글 수 = {comment_count_int}")
        self.is_under_comment_limit = comment_count_int <= MAX_EXISTING_COMMENTS

    def _type_like_human(self, element, text):
        """
        사람처럼 자연스럽게 한 글자씩 타이핑

        각 문자를 순차적으로 입력하며 글자 사이에 랜덤 지연을 추가하여
        사람의 타이핑 패턴을 모방합니다.

        Args:
            element: Selenium WebElement (텍스트를 입력할 대상 요소)
            text: 입력할 텍스트 문자열
        """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.2))

    def add_comment(self, header: str, content: str):
        """
        댓글을 작성하고 등록 성공 여부를 반환

        Args:
            header: 블로그 게시글 제목
            content: 블로그 게시글 본문 (토큰 제한 적용됨)

        Returns:
            bool: 댓글 작성 성공 여부
        """
        # 1. 댓글 버튼 클릭하여 입력창 활성화
        self.btn_comment.click()
        wait_random()

        # 2. 댓글 입력창이 나타날 때까지 대기
        u_cbox_write_box = WebDriverWait(self.driver_manager.get_driver(), 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".u_cbox_write_box"))
        )

        # 3. 댓글 입력창 확인 후 OpenAI API로 댓글 생성
        text = generate_comment(header, content)

        # 4. 댓글 입력 영역에 사람처럼 타이핑하여 텍스트 입력
        write_area = u_cbox_write_box.find_element(
            By.CSS_SELECTOR, '.u_cbox_inbox div[contenteditable="true"]'
        )
        self._type_like_human(write_area, text)

        # 5. 댓글 등록 버튼 클릭
        u_cbox_btn_upload = u_cbox_write_box.find_element(
            By.CSS_SELECTOR, ".u_cbox_upload .u_cbox_btn_upload"
        )
        u_cbox_btn_upload.click()
        wait_random(min_sec=2, max_sec=4)

        # 6. 댓글 작성 성공 여부 확인
        # 작성된 댓글 목록에서 내 블로그 ID가 있는지 확인
        post_1 = self.driver_manager.get_driver().find_element(By.ID, "post_1")
        u_cbox_names = post_1.find_elements(
            By.CSS_SELECTOR, ".u_cbox_content_wrap ul li a.u_cbox_name"
        )
        is_success = any(
            a.get_attribute("href").split("/")[-1] == MY_BLOG_ID for a in u_cbox_names
        )
        logger.info(f"댓글 등록 성공 여부 = {is_success}")

        return is_success
