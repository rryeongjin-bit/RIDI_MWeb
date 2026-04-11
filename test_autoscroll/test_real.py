from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from test_common import *


# ============================================================
# 설정 
# ============================================================
PLATFORM    = "ios"     # "android" or "ios"
IS_SIMULATOR = True     # iOS 시뮬레이터 여부 (Android는 무관)

# ============================================================
# Android 실기기
# ============================================================
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

# ============================================================
# iOS 실기기 / 시뮬레이터
# ============================================================
def get_ios_caps():
    options = XCUITestOptions()
    caps = {
        "platformName":   "iOS",
        "bundleId":       "com.initialcoms.ridi.staging",
        "noReset":        True,
        "automationName": "XCUITest",
    }
    if IS_SIMULATOR:
        caps["deviceName"] = "iPhone 15 Pro"
        caps["udid"]       = "your-simulator-uuid"  # xcrun simctl list | grep Booted
    else:
        caps["deviceName"] = "your_device_name"
        caps["udid"]       = "your-device-udid"     # instruments -s devices
    options.load_capabilities(caps)
    return options

# ============================================================
# 실행
# ============================================================
def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
        device_name = "android_device"
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())
        device_name = "ios_device"

    try:
        measure_auto_scroll_speed(driver, speed_label="1.0x",
                                  platform=PLATFORM, device_name=device_name)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()