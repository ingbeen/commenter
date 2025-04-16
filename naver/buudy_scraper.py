from selenium.webdriver.common.by import By
from common.base_driver import BaseDriver
from common.log_utils import logger
from common.time_utils import wait_random


class BuddyScraper(BaseDriver):
    def __init__(self, driver):
        super().__init__(driver)
    

    def get_recent_posting_buddy_ids(self) -> list[str]:
        page = 1
        limit = 100
        collected_ids = set()

        self._go_to_buddy_manage()
        buddysel_order = self.driver.find_element(By.ID, "buddysel_order")
        buddysel_order.click()
        wait_random()

        newpost = buddysel_order.find_elements(By.CSS_SELECTOR, 'option[value="newpost"]')
        newpost.click()
        wait_random()

        buddysel_buudyall = self.driver.find_element(By.ID, "buddysel_buudyall")
        buddysel_buudyall.click()
        wait_random()

        mutual_buddy = buddysel_buudyall.find_elements(By.CSS_SELECTOR, 'option[value="1"]')
        mutual_buddy.click()
        wait_random()

        while len(collected_ids) < limit:
            table = self.driver.find_element(By.ID, "tableListById")
            blog_id_elements = table.find_elements(By.CSS_SELECTOR, "span.blogid")

            for el in blog_id_elements:
                blog_id = el.text.strip()
                if blog_id and blog_id != "smy375":
                    collected_ids.add(blog_id)

            logger.info(f"len(collected_ids) = {len(collected_ids)}")
            page += 1
        
        return list(collected_ids)

    def _go_to_buddy_manage(self):
        url = (f"https://admin.blog.naver.com/smy375/buddy/manage")
        self.get(url)
