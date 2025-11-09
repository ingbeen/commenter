import os

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from common.time_utils import wait_random


class DriverManager:
    """
    Selenium WebDriver 생명주기를 관리하는 클래스

    Chrome WebDriver를 생성, 재시작, 종료하는 역할을 담당합니다.
    사용자 데이터 디렉토리를 지정하여 로그인 세션을 유지하고,
    Chrome 로그를 억제하여 콘솔 출력을 깔끔하게 유지합니다.

    Attributes:
        driver (WebDriver): Selenium Chrome WebDriver 인스턴스
    """

    def __init__(self):
        """
        DriverManager 초기화

        Chrome WebDriver를 생성하여 driver 속성에 저장합니다.
        """
        self.driver = self._create_chrome_driver()

    def restart_driver(self):
        """
        WebDriver를 재시작

        현재 WebDriver를 종료하고 새로운 WebDriver를 생성합니다.
        종료 후 랜덤 대기 시간을 두어 자연스러운 재시작을 구현합니다.
        """
        if self.driver:
            self.driver.quit()
            wait_random()
        self.driver = self._create_chrome_driver()

    def get_driver(self) -> WebDriver:
        """
        WebDriver 인스턴스를 반환

        Returns:
            WebDriver: 현재 활성화된 Chrome WebDriver 인스턴스

        Raises:
            RuntimeError: Driver가 초기화되지 않은 경우
        """
        if self.driver is None:
            raise RuntimeError("Driver is not initialized.")
        return self.driver

    def quit(self):
        """
        WebDriver를 종료하고 리소스 정리

        Driver를 종료하고 driver 속성을 None으로 설정합니다.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _create_chrome_driver(self):
        """
        Chrome WebDriver를 생성 (내부 메서드)

        사용자 데이터 디렉토리를 지정하여 로그인 세션을 유지하고,
        Chrome 로그를 억제하는 옵션을 적용합니다.

        Returns:
            WebDriver: 설정이 적용된 Chrome WebDriver 인스턴스
        """
        options = webdriver.ChromeOptions()

        custom_user_data = r"C:\chrome-driver\chrome-user-data"
        os.makedirs(custom_user_data, exist_ok=True)
        options.add_argument(f"--user-data-dir={custom_user_data}")

        # Chrome 로그 억제 (콘솔 ERROR 메시지 제거)
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return webdriver.Chrome(options=options)
