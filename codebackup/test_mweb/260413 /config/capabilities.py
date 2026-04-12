from config.settings import *

def _build_caps(base: dict, udid: str) -> dict:
    """UDID가 있을 때만 caps에 추가"""
    if udid:
        base["appium:udid"] = udid
    return base


# Chrome 공통 옵션 (번역 팝업 등 불필요한 UI 비활성화)
CHROME_OPTIONS = {
    "goog:chromeOptions": {
        "args": [
            "--disable-translate",           # 번역 비활성화
            "--no-first-run",                # 첫 실행 안내 비활성화
            "--disable-popup-blocking",      # 팝업 차단 비활성화
            "--lang=ko",                     # 언어 한국어 고정
            "--disable-features=TranslateUI",# 번역 UI 완전 비활성화
        ]
    }
}


# Android Emulator 
AOS_EMULATOR_CHROME = _build_caps({
    "appium:serverUrl":          get_appium_url("aos_emulator"),
    "platformName":              "Android",
    "appium:automationName":     "UiAutomator2",
    "appium:deviceName":         AOS_DEVICE["emulator"]["device_name"],
    "browserName":               "Chrome",
    "appium:noReset":            True,
    "appium:newCommandTimeout":  TIMEOUT["new_command"],
    "appium:adbExecTimeout": TIMEOUT["adb_exec"],
    **CHROME_OPTIONS,
}, udid=AOS_DEVICE["emulator"]["udid"])


# # Android Real Device
# AOS_REAL_CHROME = _build_caps({
#     "appium:serverUrl":          get_appium_url("aos_real"),
#     "platformName":              "Android",
#     "appium:automationName":     "UiAutomator2",
#     "appium:deviceName":         AOS_DEVICE["real"]["device_name"],
#     "browserName":               "Chrome",
#     "appium:noReset":            True,
#     "appium:newCommandTimeout":  TIMEOUT["new_command"],
#     "appium:adbExecTimeout": TIMEOUT["adb_exec"],
#     **CHROME_OPTIONS,
# }, udid=AOS_DEVICE["real"]["udid"])

# AOS_REAL_SAMSUNG = _build_caps({
#     "appium:serverUrl":              get_appium_url("aos_real"),
#     "platformName":                  "Android",
#     "appium:automationName":         "UiAutomator2",
#     "appium:deviceName":             AOS_DEVICE["real"]["device_name"],
#     "browserName":                   "Samsung Internet",
#     "appium:chromedriverExecutable": CHROMEDRIVER_PATH,
#     "appium:noReset":                True,
#     "appium:newCommandTimeout":      TIMEOUT["new_command"],
#     "appium:adbExecTimeout": TIMEOUT["adb_exec"],
# }, udid=AOS_DEVICE["real"]["udid"])

# iOS Simulator 
IOS_SIMULATOR_SAFARI = _build_caps({
    "appium:serverUrl":          get_appium_url("ios_simulator"),
    "platformName":              "iOS",
    "appium:automationName":     "XCUITest",
    "appium:deviceName":         IOS_DEVICE["simulator"]["device_name"],
    "appium:platformVersion":    IOS_DEVICE["simulator"]["platform_version"],
    "browserName":               "Safari",
    "appium:noReset":            True,
    "appium:newCommandTimeout":  TIMEOUT["new_command"],
    "appium:adbExecTimeout": TIMEOUT["adb_exec"],
}, udid=IOS_DEVICE["simulator"]["udid"])

# IOS_SIMULATOR_CHROME = _build_caps({
#     "appium:serverUrl":          get_appium_url("ios_simulator"),
#     "platformName":              "iOS",
#     "appium:automationName":     "XCUITest",
#     "appium:deviceName":         IOS_DEVICE["simulator"]["device_name"],
#     "appium:platformVersion":    IOS_DEVICE["simulator"]["platform_version"],
#     "browserName":               "Chrome",
#     "appium:noReset":            True,
#     "appium:newCommandTimeout":  TIMEOUT["new_command"],
#     "appium:adbExecTimeout": TIMEOUT["adb_exec"],
#     **CHROME_OPTIONS,
# }, udid=IOS_DEVICE["simulator"]["udid"])

# # iOS Real Device
# IOS_REAL_SAFARI = _build_caps({
#     "appium:serverUrl":          get_appium_url("ios_real"),
#     "platformName":              "iOS",
#     "appium:automationName":     "XCUITest",
#     "appium:deviceName":         IOS_DEVICE["real"]["device_name"],
#     "appium:platformVersion":    IOS_DEVICE["real"]["platform_version"],
#     "browserName":               "Safari",
#     "appium:noReset":            True,
#     "appium:newCommandTimeout":  TIMEOUT["new_command"],
#     "appium:adbExecTimeout": TIMEOUT["adb_exec"],
#     "appium:startIWDP":          True,
# }, udid=IOS_DEVICE["real"]["udid"])

# IOS_REAL_CHROME = _build_caps({
#     "appium:serverUrl":          get_appium_url("ios_real"),
#     "platformName":              "iOS",
#     "appium:automationName":     "XCUITest",
#     "appium:deviceName":         IOS_DEVICE["real"]["device_name"],
#     "appium:platformVersion":    IOS_DEVICE["real"]["platform_version"],
#     "browserName":               "Chrome",
#     "appium:noReset":            True,
#     "appium:newCommandTimeout":  TIMEOUT["new_command"],
#     "appium:adbExecTimeout": TIMEOUT["adb_exec"],
#     "appium:startIWDP":          True,
#     **CHROME_OPTIONS,
# }, udid=IOS_DEVICE["real"]["udid"])

# 마커 > Capabilities 매핑 
# conftest.py에서 마커를 읽어 해당 Capabilities 선택 시 사용
CAPS_MAP = {
    ("aos",  "emulator",  "chrome"):  AOS_EMULATOR_CHROME,
    # ("aos",  "real",      "chrome"):  AOS_REAL_CHROME,
    # ("aos",  "real",      "samsung"): AOS_REAL_SAMSUNG,
    ("ios",  "simulator", "safari"):  IOS_SIMULATOR_SAFARI,
    #("ios",  "simulator", "chrome"):  IOS_SIMULATOR_CHROME,
    # ("ios",  "real",      "safari"):  IOS_REAL_SAFARI,
    # ("ios",  "real",      "chrome"):  IOS_REAL_CHROME,
}