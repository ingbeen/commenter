from selenium.webdriver.common.by import By
from common.base_driver import BaseDriver
from common.time_utils import wait_random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.log_utils import logger

class CommentWriter(BaseDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.can_add_comment = False
        self.btn_comment = None

    def press_like_if_needed(self):
        post_1 = self.driver.find_element(By.ID, "post_1")
        area_sympathy = post_1.find_element(By.CSS_SELECTOR, ".area_sympathy")
        u_likeit_list_module = area_sympathy.find_element(By.CSS_SELECTOR, ":scope > .u_likeit_list_module")
        u_likeit_list_btn = u_likeit_list_module.find_element(By.CSS_SELECTOR, "a.u_likeit_list_btn")
        if "on" in u_likeit_list_btn.get_attribute("class").split():
            logger.info(f"공감 버튼 눌러져 있음")
            return
        
        u_likeit_list_btn.click()
        logger.info(f"공감 버튼 클릭")
        self.can_add_comment = True
        wait_random()

    def init_comment_button (self):
        post_1 = self.driver.find_element(By.ID, "post_1")
        self.btn_comment = post_1.find_element(By.CSS_SELECTOR, ".area_comment .btn_comment")

    def add_comment(self, text: str):
        self.btn_comment.click()
        wait_random()

        u_cbox_write_box = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".u_cbox_write_box"))
        )

        label_area = u_cbox_write_box.find_element(By.CSS_SELECTOR, '.u_cbox_inbox label')
        label_area.click()
        wait_random()
        
        write_area = u_cbox_write_box.find_element(By.CSS_SELECTOR, '.u_cbox_inbox div[contenteditable="true"]')
        write_area.send_keys(text)

        u_cbox_btn_upload = u_cbox_write_box.find_element(By.CSS_SELECTOR, ".u_cbox_upload .u_cbox_btn_upload")
        u_cbox_btn_upload.click()
        logger.info(f"댓글 등록 버튼 클릭")
        wait_random(min_sec=4, max_sec=6)
