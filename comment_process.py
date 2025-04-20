from api.generate_comment import generate_comment, truncate_text_to_token_limit, is_token_length_valid
from driver.driver_manager import DriverManager
from naver.comment_writer import CommentWriter
from naver.comment_scraper import CommentScraper
from naver.buddy_scraper import BuddyScraper
from naver.blog_scraper import BlogScraper
from common.log_utils import error_log, logger
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
import sys

class CommentProcessor:
    def __init__(self, driver_manager: DriverManager):
        self.driver_manager = driver_manager
        self.repeat_count = 0
        self.success_count = 0
        self.alert_count = 0
    
    def _process_single_blog(self, blog_id, blog_scraper):
        self.repeat_count += 1
        
        try:
            url = blog_scraper.go_to_blog(blog_id)
            header = blog_scraper.get_post_header()
            content = blog_scraper.get_post_content()
            content = truncate_text_to_token_limit(content)

            if not is_token_length_valid(content):
                logger.info("본문 글자수 적음")
                return

            comment_writer = CommentWriter(self.driver_manager)
            comment_writer.press_like_if_needed()
            comment_writer.init_comment_button()
            comment_writer.set_can_add_comment()

            if not comment_writer.did_press_like or not comment_writer.is_under_comment_limit:
                logger.info("댓글 등록 제외")
                return

            comment = generate_comment(header, content)
            is_success = comment_writer.add_comment(comment)
            if is_success:
                self.success_count += 1
        except UnexpectedAlertPresentException as e:
            alert = self.driver_manager.get_driver().switch_to.alert
            alert_text = alert.text
            error_log(e, url)
            alert.accept()
            self.alert_count += 1

            if "더이상 등록할 수 없습니다" in alert_text or self.alert_count >= 5:
                self.driver_manager.quit()
                sys.exit("자동화 중단: 댓글 제한 도달")
        except NoSuchElementException as e:
            if '[id="post_1"]' in str(e) or 'id="post_1"' in str(e):
                logger.info("pass / post_1 없음")
            elif '.area_sympathy' in str(e) or 'class="area_sympathy"' in str(e):
                logger.info("pass / area_sympathy 없음")
            elif '.area_comment .btn_comment' in str(e) or 'class="btn_comment"' in str(e):
                logger.info("pass / btn_comment 없음")
            else:
                error_log(e, url)
        except Exception as e:
            error_log(e, url)

    def _process_loop_blog(self, recent_commenter_ids):
        blog_scraper = BlogScraper(self.driver_manager)
        last_restart_at = 0

        for blog_id in recent_commenter_ids:
            self._process_single_blog(blog_id, blog_scraper)
            logger.info(f"repeat_count = {self.repeat_count} / success_count = {self.success_count}")
            
            should_restart = (
                self.success_count != 0 and
                self.success_count % 30 == 0 and
                self.success_count != last_restart_at
            )
            if should_restart:
                last_restart_at = self.success_count
                self.driver_manager.restart_driver()

    def run(self):
        comment_scraper = CommentScraper(self.driver_manager)
        recent_commenter_ids = comment_scraper.get_recent_commenter_ids()
        logger.info(f"최근 댓글 등록한 아이디 = {recent_commenter_ids}")
        
        self._process_loop_blog(recent_commenter_ids)

        buddy_scraper = BuddyScraper(self.driver_manager)
        recent_posting_buddy_ids = buddy_scraper.get_recent_posting_buddy_ids()
        logger.info(f"서로이웃 중 최근 글 등록한 아이디 = {recent_posting_buddy_ids}")
        
        self._process_loop_blog(recent_posting_buddy_ids)