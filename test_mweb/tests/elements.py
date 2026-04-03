from selenium.webdriver.common.by import By
from config.settings import *

class URLs:
    HOME  = BASE_URL
    LOGIN = f"{BASE_URL}/account/login"
    
    # aos
    CONTENT_HOME_ALL_AOS = f"https://ridibooks.com/books/5847000001"  # 웹툰 > 두 명의 상속인
    CONTENT_HOME_ADULT_AOS = f"https://ridibooks.com/books/2057208584"  # 웹소설 > 꽃은 밤을 걷는다

    CONTENT_ALL_VIEW_AOS = f"https://ridibooks.com/books/5847000004/view"
    CONTENT_ADULT_VIEW_AOS = f"https://ridibooks.com/books/2057208587/view"

    #ios
    CONTENT_HOME_ALL_IOS = f"https://ridibooks.com/books/1518000665"  # 웹툰 > 카야
    CONTENT_HOME_ADULT_IOS = f"https://ridibooks.com/books/3885042618"  # 웹소설 > 히든 피스 메이커

    CONTENT_ALL_VIEW_IOS = f"https://ridibooks.com/books/1518000668/view"
    CONTENT_ADULT_VIEW_IOS = f"https://ridibooks.com/books/3885043404/view"

class GenreHome:
    MAIN_LOGIN_AOS = (By.CSS_SELECTOR, '#__next > div.fig-6bprg0 > header > nav > div > div:nth-child(3) > a')
    MAIN_LOGIN_IOS = (By.CLASS_NAME, 'fig-10qv71b')

class LoginPage:
    ID_INPUT  = (By.CSS_SELECTOR, "input[name='username']")
    PW_INPUT  = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "#__next > div > section > div > form.fig-gx0lhm > button")

class LoginData:
    valid_aos =  {
        "id": "4qatest",
        "pw": "qwer1234!",
    }

    valid_ios =  {
        "id": "ridiadmin",
        "pw": "ridi0331!",
    }

class ContentHome:
    EPISODE = "4화"  # 화수 변경 시 여기만 수정
    RENT_BTN = (By.CSS_SELECTOR, f"button[data-book-title*='{EPISODE}'].serial_book_rent_button")
    BUY_BTN  = (By.CSS_SELECTOR, f"button[data-book-title*='{EPISODE}'].serial_book_buy_button")

class PaymentPopup:
    FREE_COUPON_HEADER = (By.XPATH, "//*[contains(@class, 'header_title') and contains(text(), '무료이용권')]")
    PAYMENT_METHOD_BTN = (By.CLASS_NAME, "text_button js_show_another_payment")

    PAYMENT_HEADER = (By.XPATH, "//*[contains(@class, 'header_title') and contains(text(), '결제하기')]")
    PAYMENT_BTN = (By.XPATH, "//*[contains(@class, 'rui_button_blue_40 rui_button_eink_black_40 blue_button js_payment_book_cash_and_point_immediate_view') and contains(text(), '결제하고 바로보기')")