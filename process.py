# process.py

from api.generate_comment import generate_comment, truncate_text_to_token_limit, is_token_length_valid
from naver.comment_writer import CommentWriter
from naver.comment_scraper import CommentScraper
from naver.buddy_scraper import BuddyScraper
from naver.blog_scraper import BlogScraper
from common.log_utils import error_log, logger
from selenium.common.exceptions import NoSuchElementException

def _process_single_blog(driver, blog_id, blog_scraper):
    try:
        url = blog_scraper.go_to_blog(blog_id)
        header = blog_scraper.get_post_header()
        content = blog_scraper.get_post_content()
        content = truncate_text_to_token_limit(content)

        if not is_token_length_valid(content):
            logger.info("pass / is_token_length_valid = False")
            return False

        comment_writer = CommentWriter(driver)
        comment_writer.press_like_if_needed()
        comment_writer.init_comment_button()

        if not comment_writer.can_add_comment:
            logger.info("pass / can_add_comment = False")
            return False

        comment = generate_comment(header, content)
        comment_writer.add_comment(comment)

        return True
    except NoSuchElementException as e:
        if '[id="post_1"]' in str(e) or 'id="post_1"' in str(e):
            logger.info("pass / post_1 없음")
        elif '.area_sympathy' in str(e) or 'class="area_sympathy"' in str(e):
            logger.info("pass / area_sympathy 없음")
        elif '.area_comment .btn_comment' in str(e) or 'class="btn_comment"' in str(e):
            logger.info("pass / btn_comment 없음")
        else:
            error_log(e, url)
        return False
    except Exception as e:
        error_log(e, url)
        return False


def _process_loop_blog(driver, recent_commenter_ids):
    repeat_count = 0
    success_count = 0
    blog_scraper = BlogScraper(driver)

    for blog_id in recent_commenter_ids:
        repeat_count += 1
        is_success  = _process_single_blog(driver, blog_id, blog_scraper)
        if is_success:
            success_count += 1
        logger.info(f"repeat_count = {repeat_count} / success_count = {success_count}")


def process_comments(driver):
    comment_scraper = CommentScraper(driver)
    recent_commenter_ids = comment_scraper.get_recent_commenter_ids()
    logger.info(f"recent_commenter_ids = {recent_commenter_ids}")

    _process_loop_blog(driver, recent_commenter_ids)

    buddy_scraper = BuddyScraper(driver)
    recent_posting_buddy_ids = buddy_scraper.get_recent_posting_buddy_ids()
    logger.info(f"recent_posting_buddy_ids = {recent_posting_buddy_ids}")

    _process_loop_blog(driver, recent_posting_buddy_ids)