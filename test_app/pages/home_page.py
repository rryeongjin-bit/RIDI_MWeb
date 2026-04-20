from pages.base_page import *
from pages.locators import *

class Alertnotification(BasePage):
    def click_noti_alert(self):
        self.click(CommonLocators.ALLOW_BTN)

class MainhomePage(BasePage):
    def click_my_btn(self):
        self.click(MainhomeLocators.MY_BTN)
    