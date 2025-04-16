from naver.driver_factory import create_chrome_driver
from common.log_utils import error_log
from process import process_comments

def run():
    driver = None
    try:
        driver = create_chrome_driver()
        process_comments(driver)
    except Exception as e:
        error_log(e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run()