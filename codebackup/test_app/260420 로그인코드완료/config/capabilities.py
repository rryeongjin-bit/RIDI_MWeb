from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from config.settings import *

# 기기 설정 (포트 - 기기 매핑)
DEVICE_CONFIG = {
    "aos": [
        {
            "port":        4723,
            "udid":        "emulator-5554",
            "device_name": "Android Emulator",
            "os_version":  "16.0",
            "type":        "emulator",
        },
        {
            "port":        4724,
            "udid":        "YOUR_AOS_UDID_1",
            "device_name": "Galaxy S23",
            "os_version":  "13.0",
            "type":        "real",          # real | emulator
        }
    ],

    "ios": [
        {
            "port":        4725,
            "udid":        "YOUR_IOS_UDID_1",
            "device_name": "iPhone 15",
            "os_version":  "17.0",
            "type":        "real",          # real | simulator
        },
        {
            "port":        4726,
            "udid":        "YOUR_SIMULATOR_UDID",
            "device_name": "iPhone 15 Simulator",
            "os_version":  "17.0",
            "type":        "simulator",
        }
    ]
}


# -------------------------------------------------------
# Capabilities 생성
# -------------------------------------------------------
def get_capabilities(platform: str, device: dict):
    """
    플랫폼과 기기 정보를 받아 Appium Capabilities 반환

    :param platform: "aos" | "ios"
    :param device:   DEVICE_CONFIG 내 기기 딕셔너리
    :return:         UiAutomator2Options | XCUITestOptions
    """
    if platform == "aos":
        return _get_aos_capabilities(device)
    elif platform == "ios":
        return _get_ios_capabilities(device)
    else:
        raise ValueError(f"[capabilities] 지원하지 않는 플랫폼: {platform}")


def _get_aos_capabilities(device: dict) -> UiAutomator2Options:
    options = UiAutomator2Options()

    options.platform_name    = "Android"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.platform_version = device["os_version"]
    options.automation_name  = "UiAutomator2"

    # 하이브리드 앱 설정
    options.app_package      = APP_PACKAGE
    options.app_activity     = APP_ACTIVITY

    # 이미 설치된 앱 실행 (재설치 없음)
    options.no_reset         = True
    options.full_reset        = False

    # 에뮬레이터 추가 설정
    if device["type"] == "emulator":
        options.is_headless  = False        # 에뮬레이터 UI 표시

    return options


def _get_ios_capabilities(device: dict) -> XCUITestOptions:
    options = XCUITestOptions()

    options.platform_name    = "iOS"
    options.device_name      = device["device_name"]
    options.udid             = device["udid"]
    options.platform_version = device["os_version"]
    options.automation_name  = "XCUITest"

    # 하이브리드 앱 설정
    options.bundle_id        = BUNDLE_ID_IOS

    # 이미 설치된 앱 실행 (재설치 없음)
    options.no_reset         = True
    options.full_reset        = False

    # 시뮬레이터 추가 설정
    if device["type"] == "simulator":
        options.is_simulator = True

    return options


# -------------------------------------------------------
# Appium Server URL 생성
# -------------------------------------------------------
def get_server_url(port: int) -> str:
    """
    포트 번호를 받아 Appium Server URL 반환

    :param port: 기기별 Appium 서버 포트
    :return:     Appium Server URL 문자열
    """
    return f"http://localhost:{port}"