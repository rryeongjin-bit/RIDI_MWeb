import pytest
from config.settings import *
from tests.elements import *
from utils.helpers import *
from selenium.common.exceptions import TimeoutException

"""Selenium WebDriver 기반으로 실행 """

pytestmark = [
    pytest.mark.aos,
    pytest.mark.ios,
    pytest.mark.real,
    pytest.mark.emulator,
    pytest.mark.simulator,
    pytest.mark.chrome,
    pytest.mark.samsung,
    pytest.mark.safari,
]

class TestLogin:
    @pytest.mark.order(1)
    def test_login(self, logged_in): 
        assert "account/login" not in logged_in.current_url, \
            f"❌ 로그인 실패. 현재 URL: {logged_in.current_url}"
        
class TestContenthomeAll:
    """전연령작품 회차목록 > 4화 대여결제 및 뷰어진입 """
    @pytest.mark.order(2)
    def test_contenthome_all(self, logged_in): 
        driver = logged_in
        driver.get(URLs.CONTENT_HOME_ALL)

        btn_rent = wait_for_element_clickable(driver, ContentHome.RENT_BTN)
        scroll_to_center_element(driver, btn_rent)
        wait_seconds(3)

        tap_element(driver, btn_rent)
        if is_chrome(driver):
            wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
            payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_METHOD_BTN)
            tap_element(driver, payment_method_btn)

        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        btn_payment = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_BTN)
        tap_element(driver, btn_payment)
        wait_for_url_contains(driver, URLs.CONTENT_ALL_VIEW)
        wait_seconds(3)
        assert URLs.CONTENT_ALL_VIEW in driver.current_url, \
            f"❌ 뷰어 진입 실패"

class TestViewerAll:
    """ 전연령작품 뷰어진입 및 다음화 결제 """
    @pytest.mark.order(3)
    def test_viewer_all(self, logged_in): 
        driver = logged_in
        driver.get(URLs.CONTENT_ALL_VIEW)
        wait_seconds(3)

        btn_next= wait_for_element_clickable(driver, Viewer.NEXT_BTN)
        tap_element(driver, btn_next)
        wait_for_element_visible(driver, PaymentPopup.SELECT_PAYMENT_HEADER)
        
        btn_rent_nextcontent = wait_for_element_clickable(driver, PaymentPopup.RENT_NEXT_BTN)
        tap_element(driver, btn_rent_nextcontent)
        if is_chrome(driver):
            wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
            next_payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_METHOD_BTN)
            tap_element(driver, next_payment_method_btn)
        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        btn_next_payment = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_BTN)
        tap_element(driver, btn_next_payment)
        wait_for_url_contains(driver, URLs.CONTENT_ALL_NEXTVIEW)
        assert URLs.CONTENT_ALL_NEXTVIEW in driver.current_url, \
            f"❌ 다음화 뷰어 진입 실패"

class TestContenthomeAdult:
    """성인작품 회차목록 > 4화 대여결제 및 뷰어진입 """
    @pytest.mark.order(4)
    def test_contenthome_adult(self, logged_in): 
        driver = logged_in
        driver.get(URLs.CONTENT_HOME_ADULT)
        wait_seconds(3)

        btn_buy = wait_for_element_clickable(driver, ContentHome.BUY_BTN)
        scroll_to_center_element(driver, btn_buy)
        wait_seconds(3)

        tap_element(driver, btn_buy)
        if is_chrome(driver):
            wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
            payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_METHOD_BTN)
            tap_element(driver, payment_method_btn)

        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        btn_payment = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_BTN)
        tap_element(driver, btn_payment)
        wait_for_url_contains(driver, URLs.CONTENT_ADULT_VIEW)
        assert URLs.CONTENT_ADULT_VIEW in driver.current_url, \
            f"❌ 뷰어 진입 실패"

class TestViewerAdult:
    """ 성인작품 뷰어진입 및 다음화 결제 """
    @pytest.mark.order(5)
    def test_viewer_adult(self, logged_in): 
        driver = logged_in
        driver.get(URLs.CONTENT_ADULT_VIEW)
        wait_seconds(3)

        btn_next= wait_for_element_clickable(driver, Viewer.NEXT_BTN)
        tap_element(driver, btn_next)

        wait_for_element_visible(driver, PaymentPopup.FREE_VIEW_HEADER)
        next_payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_METHOD_BTN)
        tap_element(driver, next_payment_method_btn)

        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        btn_next_payment = wait_for_element_clickable(driver, PaymentPopup.NEXT_PAYMENT_BTN)

        tap_element(driver, btn_next_payment)
        wait_for_url_contains(driver, URLs.CONTENT_ADULT_NEXTVIEW)
        assert URLs.CONTENT_ADULT_NEXTVIEW in driver.current_url, \
            f"❌ 다음화 뷰어 진입 실패"

class TestCart:
    """ 회차목록 > 카트담기 """
    @pytest.mark.order(6)
    def test_cart(self, logged_in):
        driver = logged_in
        driver.get(URLs.CONTENT_HOME)

        select_area = wait_for_element_visible(driver, ContentHome.SELECT_ALL)
        scroll_to_center_element(driver, select_area)
        wait_seconds(3)
        
        checkbox_first = wait_for_element(driver, ContentHome.FIRST_EPISODE_CHECKBOX)
        tap_element(driver, checkbox_first)

        btn_cart = wait_for_element_clickable(driver, ContentHome.CART_BTN)
        tap_element(driver, btn_cart)

        try:
            toast_msg = wait_for_element_visible(driver, ContentHome.TOAST_MSG_CART, timeout=5)
            assert toast_msg.is_displayed(), "❌ 카트담기 실패"
        except TimeoutException:
            assert False, "❌ 카트담기 토스트 메시지 미노출"
        
class TestCartPayment:
    """ 카트 소장탭 > 작품 구매 """
    @pytest.mark.order(7)
    def test_cartpage(self, logged_in):
        driver = logged_in
        driver.get(URLs.CART)

        buy_tab = wait_for_element(driver, CartPage.BUY_TAB)
        if "selected" in buy_tab.get_attribute("class"):
            print("소장가능 탭 활성화 상태")
        else:
            tap_element(driver, buy_tab)
            wait_for_element_visible(driver, CartPage.BUY_TAB_SELECTED)
            print("소장가능 탭 선택 및 활성화")
        assert "selected" in buy_tab.get_attribute("class"), \
            "소장가능 탭이 활성화되지 않았습니다."

        checkbox_all = wait_for_element_clickable(driver, CartPage.SELECT_ALL_CHECKBOX)
        tap_element(driver, checkbox_all)

        checkbox_first = wait_for_element(driver, CartPage.FIRST_CONTENTS_CHECKBOX)
        tap_element(driver, checkbox_first)

        btn_buy = wait_for_element_clickable(driver, CartPage.BUY_BTN)
        tap_element(driver, btn_buy)

        wait_for_url_contains(driver, URLs.CHECKPOUT)
        assert URLs.CHECKPOUT in driver.current_url, \
            f"❌ 결제페이지 진입 실패"

        togle_agree_payment = wait_for_element_clickable(driver, CheckoutPage.PAYMENT_AGREE_TOGGLE)
        btn_payment = wait_for_element_clickable(driver, CheckoutPage.PAYMENT_BTN)
        tap_element(driver, togle_agree_payment)
        tap_element(driver, btn_payment)

        complete_payment = wait_for_element_visible(driver, CheckoutPage.PAYMENT_COMPLETE)
        assert complete_payment.is_displayed(), "❌ 카트 결제 실패"

class Testgift:
    """ 선물하기 """
    @pytest.mark.order(8)
    def test_gift(self, logged_in):
        driver = logged_in
        driver.get(URLs.CONTENT_GIFT)

        btn_gift = wait_for_element_clickable(driver,ContentHome.GIFT_BTN)
        tap_element(driver, btn_gift)
        wait_for_url_contains(driver, URLs.GIFT)
        assert URLs.GIFT in driver.current_url, \
            f"❌ 선물하기 결제페이지 진입 실패"

class TestGiftPayment:
    """ 카트 소장탭 > 작품 구매 """
    @pytest.mark.order(9)
    def test_giftpage(self, logged_in):
        driver = logged_in
        driver.get(URLs.GIFT)

        receiver_area = wait_for_element_visible(driver, GiftPage.RECEIVER_AREA)
        scroll_to_center_element(driver, receiver_area)

        input_sender = wait_for_element_clickable(driver, GiftPage.SENDER)
        tap_element(driver, input_sender)
        clear_and_input(driver, input_sender, GiftData.valid['sender'])

        input_receiver = wait_for_element_clickable(driver, GiftPage.RECEIVER)
        tap_element(driver, input_receiver)
        clear_and_input(driver, input_receiver, GiftData.valid['receiver'])

        payment_btn = wait_for_element_clickable(driver, GiftPage.GIFT_PAYMENT_BTN)
        tap_element(driver, payment_btn)
        wait_seconds(3)

        detail_payment = wait_for_element_visible(driver, CheckoutPage.GIFT_PAYMENT_DETAIL)
        scroll_to_center_element(driver, detail_payment)

        togle_agree_payment = wait_for_element_clickable(driver, CheckoutPage.PAYMENT_AGREE_TOGGLE)
        btn_payment = wait_for_element_clickable(driver, CheckoutPage.PAYMENT_BTN)
        tap_element(driver, togle_agree_payment)
        tap_element(driver, btn_payment)

        assert driver.current_url.startswith(URLs.GIFT_COMPLETE), \
            f"❌ 선물하기 결제 실패"
  
class TestLogout:
    """ 로그아웃 """
    @pytest.mark.order(10)
    def test_logout(self,logged_in):
        driver = logged_in
        driver.get(URLs.MYRIDI)
        
        btn_logout = wait_for_element_clickable(driver, MyPage.LOGOUT_BTN)
        tap_element(driver, btn_logout)

        wait_for_url_contains(driver, URLs.HOME)
        assert URLs.HOME in driver.current_url, \
            f"❌ 로그아웃 실패"
