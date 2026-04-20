import pytest
from pages.base_page import *
from pages.home_page import *
from pages.login_page import *
from data.test_data import *

pytestmark = [
    pytest.mark.aos,
    pytest.mark.ios,
    pytest.mark.real,
    pytest.mark.emulator,
    pytest.mark.simulator,
]

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, driver, platform):
        self.driver   = driver
        self.mainhome = MainhomePage(driver, platform)
        self.page     = LoginPage(driver, platform)
        self.alert    = Alertnotification(driver, platform)
        self.replace  = Replacedevicelist(driver, platform)
        self.platform = platform
        self.account  = TestAccount.AOS if platform == "aos" else TestAccount.IOS

    @pytest.mark.smoke
    def test_login_success(self):
        # 알림 허용 팝업
        if self.alert.is_displayed(CommonLocators.ALERT_ALLOW):
            self.alert.click_noti_alert()

        # MY 버튼 클릭
        self.mainhome.click_my_btn()

        # 로그인
        self.page.click_login_btn()
        self.page.login(
            id=self.account["id"],
            pw=self.account["pw"]
        )

        # 기기 교체 화면
        if self.replace.is_present(ReplacedeviceLocators.REPLACEDEVICE_LIST_TITLE):
            self.replace.click_replace_toggle()
            self.replace.click_replace_btn()

        assert self.page.is_displayed(MyLocators.MY_TITLE), \
            "❌ 로그인 실패"