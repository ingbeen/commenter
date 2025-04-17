from selenium.webdriver.common.by import By
from common.base_driver import BaseDriver
from common.constants import EXCLUDED_BLOG_IDS
from common.log_utils import logger


class CommentScraper(BaseDriver):
    def __init__(self, driver):
        super().__init__(driver)
    

    def get_recent_commenter_ids(self) -> list[str]:
        page = 1
        limit = 100
        collected_ids = set()

        while len(collected_ids) < limit:
            self._go_to_comment_manage(page)

            table = self.driver.find_element(By.ID, "tableListById")
            blog_id_elements = table.find_elements(By.CSS_SELECTOR, "span.blogid")

            for el in blog_id_elements:
                blog_id = el.text.strip()
                if blog_id and blog_id not in EXCLUDED_BLOG_IDS:
                    collected_ids.add(blog_id)

            logger.info(f"len(collected_ids) = {len(collected_ids)}")
            page += 1
        
        return list(collected_ids)

    def _go_to_comment_manage(self, page):
        url = (f"https://admin.blog.naver.com/AdminNaverCommentManageView.naver?paging.commentSearchType=0&paging.economyTotalCount=8220&paging.commentSearchValue=&blogId=smy375&paging.currentPage={page}"
        )
        self.get(url)
