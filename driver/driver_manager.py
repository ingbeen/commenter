import os
from selenium import webdriver
from common.time_utils import wait_random
from common.log_utils import logger
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service

class DriverManager:
    def __init__(self):
        self.driver = self._create_chrome_driver()

    def restart_driver(self):
        if self.driver:
            self.driver.quit()
            wait_random()
        self.driver = self._create_chrome_driver()
        logger.info("드라이버 재시작 성공")

    def get_driver(self) -> WebDriver:
        if self.driver is None:
            raise RuntimeError("Driver is not initialized.")
        return self.driver

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _create_chrome_driver(self):
        options = webdriver.ChromeOptions()

        custom_user_data = r"C:\chrome-driver\chrome-user-data"
        os.makedirs(custom_user_data, exist_ok=True)
        options.add_argument(f"--user-data-dir={custom_user_data}")

        # driver_path = r"C:\chrome-driver\chromedriver-win64\chromedriver.exe"
        # service = Service(executable_path=driver_path)

        return webdriver.Chrome(options=options)