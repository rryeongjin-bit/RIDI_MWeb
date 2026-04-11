from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from test_common import *

PLATFORM = "android"  # "android" or "ios"

def get_android_caps():
    options = UiAutomator2Options()
    options.load_capabilities({
        "platformName":   "Android",
        "deviceName":     "your_device_name",    # adb devices로 확인
        "appPackage":     "com.initialcoms.ridi.staging",
        "appActivity":    "com.initialcoms.ridi.staging.MainActivity",
        "noReset":        True,
        "automationName": "UiAutomator2",
    })
    return options

def get_ios_caps():
    options = XCUITestOptions()
    options.load_capabilities({
        "platformName":   "iOS",
        "deviceName":     "your_device_name",    # 기기명
        "udid":           "your-device-udid",    # instruments -s devices로 확인
        "bundleId":       "com.initialcoms.ridi.staging",
        "noReset":        True,
        "automationName": "XCUITest",
    })
    return options

def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())

    try:
        # is_emulator=False → screencap이 이미 물리px
        measure_auto_scroll_speed(driver, is_emulator=False)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()