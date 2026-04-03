import pytest
from config.settings import *
from tests.elements import *
from utils.helpers import *

@pytest.mark.aos
@pytest.mark.ios
@pytest.mark.real
@pytest.mark.emulator
@pytest.mark.simulator
@pytest.mark.chrome
@pytest.mark.samsung
@pytest.mark.safari
class TestLogin:
    @pytest.mark.order(1)
    def test_enter_to_loginpage(self,driver):
        driver.get(URLs.HOME)
        wait_for_page_load(driver)

        login_btn = get_element_by_platform(
                    driver,
                    HomeElements.MAIN_LOGIN_AOS,
                    HomeElements.MAIN_LOGIN_IOS
                )
        tap_element(driver, login_btn)
        wait_seconds(3)
        wait_for_url_change(driver,URLs.HOME,timeout=30)

        assert URLs.LOGIN in driver.current_url, \
        f"로그인 페이지 이동실패. 현재 URL: {driver.current_url}"

    @pytest.mark.order(2)
    def test_login(self,driver):
        driver.get(URLs.LOGIN)
        wait_for_page_load(driver)

        id_input_box = wait_for_element_clickable(driver, LoginElements.ID_INPUT)
        pw_input_box = wait_for_element_clickable(driver, LoginElements.PW_INPUT)
        login_box = wait_for_element_clickable(driver, LoginElements.LOGIN_BTN)

        tap_element(driver, id_input_box)
        clear_and_input(driver, id_input_box, LoginData.valid['id'])

        tap_element(driver, pw_input_box)
        clear_and_input(driver, pw_input_box, LoginData.valid['pw'])

        tap_element(driver, login_box)
        dismiss_save_password_popup(driver)
        wait_for_url_change(driver, URLs.LOGIN)

        assert URLs.LOGIN not in driver.current_url, \
            f"로그인 실패. 현재 URL: {driver.current_url}"
        




