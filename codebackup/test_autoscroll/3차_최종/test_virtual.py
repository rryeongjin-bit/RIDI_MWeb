
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from test_common import * 

# 설정 
PLATFORM = "android"  # "android" or "ios"

def get_android_caps():
    options = UiAutomator2Options()
    options.load_capabilities({
        "platformName":   "Android",
        "deviceName":     "emulator-5554",
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
        "deviceName":     "iPhone 15 Pro",
        "udid":           "your-simulator-uuid",  # xcrun simctl list | grep Booted
        "bundleId":       "com.initialcoms.ridi.staging",
        "noReset":        True,
        "automationName": "XCUITest",
    })
    return options

# ============================================================
# 실행
# ============================================================
def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
        device_name = "android_emulator"
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())
        device_name = "ios_simulator"

    try:
        measure_auto_scroll_speed(driver, speed_label="1.0x",
                                  platform=PLATFORM, device_name=device_name)
    finally:
        driver.quit()
