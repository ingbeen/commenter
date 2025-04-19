import os
from selenium import webdriver
from common.time_utils import wait_random
from common.log_utils import logger
from selenium.webdriver.remote.webdriver import WebDriver

class DriverManager:
    def __init__(self):
        self.driver = self._create_chrome_driver()

    def restart_driver(self):
        if self.driver:
            self.driver.quit()
            wait_random()
        self.driver = self._create_chrome_driver()
        logger.info("success_restart_driver")

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
        
        user_name = os.path.basename(os.path.expanduser("~"))
        user_data_dir = os.path.expanduser(fr"C:\Users\{user_name}\AppData\Local\Google\Chrome\User Data")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--profile-directory=Default")
        # options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return webdriver.Chrome(options=options)