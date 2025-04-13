from common.time_utils import wait_random
from common.log_utils import logger

class BaseDriver:
    def __init__(self, driver):
        self.driver = driver

    def get(self, url: str):
        self.driver.get(url)
        logger.info(f"url = {url}")
        wait_random()