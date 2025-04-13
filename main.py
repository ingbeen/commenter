from api.generate_comment import generate_comment, truncate_text_to_token_limit
from naver.comment_writer import CommentWriter
from naver.driver_factory import create_chrome_driver
from naver.comment_scraper import CommentScraper
from naver.blog_scraper import BlogScraper
from common.log_utils import error_log, logger
from selenium.common.exceptions import NoSuchElementException

def run():
    try:
        driver = create_chrome_driver()

        comment_scraper = CommentScraper(driver)
        recent_commenter_ids = comment_scraper.get_recent_commenter_ids()
        # recent_commenter_ids = ["gkdmsgml8094"]
        # recent_commenter_ids = ['srichy', 'gowlwhdk', 'youwls0412', 'wlgp8540', 'ljh8257_', 'hosanna1507', 's25246', 'byinni', 'ggoingonmom', 'ksua07', 'subagi__', 'gpwlsdlddi', 'ansgksrla', 'ac4207', 'yeviniya', 'buho3927', 'bora0619', 'esfpmeogkkaebi', 'ingbeen', 'like0916', 'ontogeny63905', 'coca713', 'avocad0ng', 'feelsogood1900', 'romanticyellow', 'intp_bean_05', 'dreminglento', 'suuhyun15', 'wkddkdd', 'sun__1004', 'ioriwife2', 'eduventurer', 'gpffps1010', 'hzqt070', 'swingandlife', 'chxeyeon', 'juicyfarm_', 'mint__02', 'jamsilmatzip', '0326_flower', 'baeteojii', 'kuovfk500h8', 'bellese58', 'home09294', 'mgr11234', 'jjojjo2mo', '01190494234', 'dpflavhxj', 'jjjinn_', 'obr1021', 'sogood91', 'jznwkzbhe7670', 'cache4free', 'hyeppening1_', 'kms3540_', 'tk5r90z1sg', 'ddudduba1', 'seyeongaah', 'bedtopia-', 'ejejm', 'arisong___', 'hoon2956', 'ill2725', 'dreaming_peach', 'drone-pliot', 'm1685', 'jiyous2-', 'yonghee1206', 'bk__bk', 'full_copy', 'wjdgkr_', 'rani_go_', 'lsch3205', 'essecurity81', 'ela0529', 'eyyy22', 'rlduaenddl97', 'jandy0423', 'dhqhf', 'todaystories', 'jdnnc', 'lovyooree', 'jjery0524', 'saklove_01', 'genie033', 'hyunsobly', 'dnfl3tp', 'kwrfiu4768f6', 'gkdmsgml8094', 'marin5011', 'vmflsxld01', 'updanda11', 'assa98yo', 'candysunhee', 'b612_hl', 'jhloveshs', 'kate3527', 'in4box', 'madelia_', 'modelaa77', 'lovelyae5', 'jin021024', 'junnylove_']
        logger.info(f"recent_commenter_ids = {recent_commenter_ids}")

        repeat_count = 0
        success_count = 0
        blog_scraper = BlogScraper(driver)
        for blog_id in recent_commenter_ids: 
            try: 
                repeat_count += 1
                url = blog_scraper.go_to_blog(blog_id)

                header = blog_scraper.get_post_header()
                content = blog_scraper.get_post_content()
                content = truncate_text_to_token_limit(content)

                comment_writer = CommentWriter(driver)
                comment_writer.press_like_if_needed()
                if not comment_writer.can_add_comment:
                    logger.info(f"pass / can_add_comment = False")
                    continue

                comment = generate_comment(header, content)
                comment_writer.add_comment_if_needed(comment)

                success_count += 1
                logger.info(f"repeat_count = {repeat_count} / success_count = {success_count}")
            except NoSuchElementException as e:
                if '[id="post_1"]' in str(e) or 'id="post_1"' in str(e):
                    logger.info(f"pass / post_1 없음")
                elif '.area_sympathy' in str(e) or 'class="area_sympathy"' in str(e):
                    logger.info("pass / area_sympathy 없음")
                else:
                    error_log(e, url)

                continue
            except Exception as e:
                error_log(e, url)
                break

    except Exception as e:
        error_log(e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run()