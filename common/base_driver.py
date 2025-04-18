from common.time_utils import wait_random
from common.log_utils import logger
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

class BaseDriver:
    def __init__(self, driver):
        self.driver = driver


    def get(self, url: str):
        try:
            self.driver.get(url)
        except UnexpectedAlertPresentException:
            try:
                alert = self.driver.switch_to.alert
                logger.info(f"alert.text = {url}")
                alert.dismiss()
                self.driver.get(url)
            except NoAlertPresentException:
                logger.info(f"NoAlertPresentException")
        logger.info(f"url = {url}")
        wait_random()