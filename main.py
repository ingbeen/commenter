from driver.driver_manager import DriverManager
from common.log_utils import error_log
from comment_process import CommentProcessor


def run():
    try:
        driver_manager = DriverManager()
        comment_processor = CommentProcessor(driver_manager)
        comment_processor.run()
    except Exception as e:
        error_log(e)
    finally:
        if driver_manager:
            driver_manager.quit()


if __name__ == "__main__":
    run()
