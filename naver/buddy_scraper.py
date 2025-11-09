from selenium.webdriver.common.by import By

from common.constants import EXCLUDED_BLOG_IDS, MY_BLOG_ID
from common.log_utils import logger
from common.time_utils import wait_random
from driver.base_driver import BaseDriver
from driver.driver_manager import DriverManager

# 서로이웃 최근 게시자 최대 수집 개수
MAX_BUDDIES_TO_COLLECT = 500


class BuddyScraper(BaseDriver):
    def __init__(self, driver_manager: DriverManager):
        super().__init__(driver_manager)
        self.buddy_list_manage = None

    def get_recent_posting_buddy_ids(self) -> list[str]:
        page = 1
        collected_ids = set()

        self._go_to_buddy_manage()
        self._switch_to_papermain_iframe()

        buddysel_order = self.buddy_list_manage.find_element(By.ID, "buddysel_order")
        buddysel_order.click()
        wait_random()

        order_items = buddysel_order.find_elements(
            By.CSS_SELECTOR, "ul.selectbox-list li"
        )
        self._click_selectbox_item_by_text(order_items, "업데이트순")

        self._switch_to_papermain_iframe()
        buddysel_buudyall = self.buddy_list_manage.find_element(
            By.ID, "buddysel_buudyall"
        )
        buddysel_buudyall.click()
        wait_random()

        buudyall_items = buddysel_buudyall.find_elements(
            By.CSS_SELECTOR, "ul.selectbox-list li"
        )
        self._click_selectbox_item_by_text(buudyall_items, "서로이웃")

        while len(collected_ids) < MAX_BUDDIES_TO_COLLECT:
            self._switch_to_papermain_iframe()
            blog_links = self.buddy_list_manage.find_elements(
                By.CSS_SELECTOR, ".tbl_buddymanage tbody td.buddy a"
            )
            for link in blog_links:
                href = link.get_attribute("href")
                if href.startswith("https://blog.naver.com/"):
                    blog_id = href.replace("https://blog.naver.com/", "").strip()
                    if blog_id and blog_id not in EXCLUDED_BLOG_IDS:
                        collected_ids.add(blog_id)

            logger.info(f"len(collected_ids) = {len(collected_ids)}")
            page += 1

            next_page_selector = f'.paginate_re a[href="javascript:goPage({page})"]'
            next_page_link = self.buddy_list_manage.find_element(
                By.CSS_SELECTOR, next_page_selector
            )

            next_page_link.click()
            wait_random()

        return list(collected_ids)

    def _go_to_buddy_manage(self):
        url = f"https://admin.blog.naver.com/{MY_BLOG_ID}/buddy/manage"
        self.get(url)

    def _click_selectbox_item_by_text(self, items, text: str):
        for item in items:
            if item.text.strip() == text:
                item.click()
                wait_random()
                break

    def _switch_to_papermain_iframe(self):
        self.driver_manager.get_driver().switch_to.default_content()
        iframe = self.driver_manager.get_driver().find_element(By.ID, "papermain")
        self.driver_manager.get_driver().switch_to.frame(iframe)
        self.buddy_list_manage = self.driver_manager.get_driver().find_element(
            By.ID, "buddyListManageForm"
        )
