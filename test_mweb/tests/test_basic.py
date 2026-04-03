import pytest
from config.settings import *
from tests.elements import *
from utils.helpers import *

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
    def test_login(self,driver):
        driver.get(URLs.LOGIN)
        wait_for_page_load(driver)

        login_data = LoginData.valid_aos if is_android(driver) else LoginData.valid_ios

        id_input_box = wait_for_element_clickable(driver, LoginPage.ID_INPUT)
        pw_input_box = wait_for_element_clickable(driver, LoginPage.PW_INPUT)
        login_box    = wait_for_element_clickable(driver, LoginPage.LOGIN_BTN)

        tap_element(driver, id_input_box)
        clear_and_input(driver, id_input_box, login_data['id'])

        tap_element(driver, pw_input_box)
        clear_and_input(driver, pw_input_box, login_data['pw'])

        tap_element(driver, login_box)
        dismiss_save_password_popup(driver)
        wait_for_url_change(driver, URLs.LOGIN)
        wait_for_page_load(driver)

        assert "account/login" not in driver.current_url, \
            f"로그인 실패. 현재 URL: {driver.current_url}"
        
class TestContenthome:
    @pytest.mark.order(2)
    def test_contenthome(self,driver):
        contents_home_all = URLs.CONTENT_HOME_ALL_AOS if is_android(driver) else URLs.CONTENT_HOME_ALL_IOS
        driver.get(contents_home_all)
        wait_for_page_load(driver)

        btn_rent = wait_for_element_clickable(driver, ContentHome.RENT_BTN)
        scroll_to_center_element(driver, btn_rent)
        wait_seconds(5)

        tap_element(driver, btn_rent)
        #AOS/iOS 결제 팝업 진입 흐름 분기 
        if is_android(driver):
            # AOS: 무료이용권 팝업 → 결제수단 버튼 클릭 → 결제 헤더 노출
            wait_for_element_visible(driver, PaymentPopup.FREE_COUPON_HEADER)
            payment_method_btn = wait_for_element_clickable(driver, PaymentPopup.PAYMENT_METHOD_BTN)
            tap_element(driver, payment_method_btn)

        # 공통: 결제 헤더 노출 확인
        wait_for_element_visible(driver, PaymentPopup.PAYMENT_HEADER)
        
        # tap_element(driver, PaymentPopup.PAYMENT_BTN)
        # viewer_contents_all = URLs.CONTENT_ALL_VIEW_AOS if is_android(driver) else URLs.CONTENT_ALL_VIEW_IOS
        # wait_for_url_contains(driver, viewer_contents_all)
        # wait_for_page_load(driver)

        # assert viewer_contents_all not in driver.current_url, \
        #     f"뷰어진입 실패. 현재 URL: {driver.current_url}"

