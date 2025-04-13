import os
from selenium import webdriver

def create_chrome_driver():
    options = webdriver.ChromeOptions()

    # 사용자 크롬 프로필 경로 (로그인 유지용)
    user_data_dir = os.path.expanduser(r"C:\Users\yblee\AppData\Local\Google\Chrome\User Data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")  # 너의 프로필명 (Default / Profile 1 등)

    options.add_argument("--start-maximized")

    # 필요시 로그 제거
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return webdriver.Chrome(options=options)