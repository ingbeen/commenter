from common.time_utils import wait_random
from common.log_utils import logger
from driver.driver_manager import DriverManager


class BaseDriver:
    """
    모든 Scraper 클래스의 기본 클래스

    WebDriver를 사용하는 모든 크롤러 클래스의 공통 기능을 제공합니다.
    URL 이동과 랜덤 대기 시간을 조합하여 자연스러운 브라우징 패턴을 구현합니다.

    Attributes:
        driver_manager (DriverManager): WebDriver 관리 객체
    """

    def __init__(self, driver_manager: DriverManager):
        """
        BaseDriver 초기화

        Args:
            driver_manager: Selenium WebDriver를 관리하는 DriverManager 인스턴스
        """
        self.driver_manager = driver_manager

    def get(self, url: str):
        """
        지정된 URL로 이동하고 랜덤 대기

        페이지 이동 후 자연스러운 브라우징을 위해 랜덤 대기 시간을 적용합니다.
        모든 URL 이동은 로그에 기록됩니다.

        Args:
            url: 이동할 URL
        """
        driver = self.driver_manager.get_driver()
        driver.get(url)
        logger.info(f"url = {url}")
        wait_random()
