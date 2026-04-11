from appium import webdriver
from appium.options.android import UiAutomator2Options
from test_common import * 


def get_caps():
    options = UiAutomator2Options()
    options.load_capabilities({
        "platformName":   "Android",
        "deviceName":     "emulator-5554",       # adb devices로 확인
        "appPackage":     "com.initialcoms.ridi.staging",
        "appActivity":    "com.initialcoms.ridi.staging.MainActivity",
        "noReset":        True,
        "automationName": "UiAutomator2",
    })
    return options

def test_auto_scroll_speed():
    driver = webdriver.Remote(APPIUM_SERVER, options=get_caps())
    try:
        # is_emulator=True → screencap 논리px를 물리px로 리사이즈
        measure_auto_scroll_speed(driver, is_emulator=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()