from selenium.webdriver.common.by import By
from config.settings import *

class URLs:
    HOME  = BASE_URL
    LOGIN = f"{BASE_URL}/account/login"

class HomeElements:
    MAIN_LOGIN_AOS = (By.CSS_SELECTOR, '#__next > div.fig-6bprg0 > header > nav > div > div:nth-child(3) > a')
    MAIN_LOGIN_IOS = (By.CLASS_NAME, 'fig-10qv71b')

class LoginElements:
    ID_INPUT  = (By.CSS_SELECTOR, 'input[name="username"]')
    PW_INPUT  = (By.CSS_SELECTOR, 'input[name="password"]')
    LOGIN_BTN = (By.CSS_SELECTOR, '#__next > div > section > div > form.fig-gx0lhm > button')

class LoginData:
    valid =  {
        "id": "4qatest",
        "pw": "qwer1234!",
    }