from common.time_utils import wait_random
from common.log_utils import logger
from driver.driver_manager import DriverManager

class BaseDriver:
    def __init__(self, driver_manager: DriverManager):
        self.driver_manager = driver_manager

    def get(self, url: str):
        driver = self.driver_manager.get_driver()
        driver.get(url)
        logger.info(f"url = {url}")
        wait_random()
