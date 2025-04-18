import os
from selenium import webdriver

def create_chrome_driver():
    options = webdriver.ChromeOptions()
    
    user_name = os.path.basename(os.path.expanduser("~"))
    user_data_dir = os.path.expanduser(fr"C:\Users\{user_name}\AppData\Local\Google\Chrome\User Data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")

    options.add_argument("--start-maximized")

    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return webdriver.Chrome(options=options)