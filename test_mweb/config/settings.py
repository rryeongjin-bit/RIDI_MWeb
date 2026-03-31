
# Appium 서버 포트 (기기별 독립 포트)
# 기기 추가/변경 시 이 곳에서만 수정
APPIUM_PORTS = {
    "aos_emulator": 4723,
    # "aos_real":     4725,
    # "ios_simulator": 4727,
    # "ios_real":     4729,
}

def get_appium_url(key: str) -> str:
    """key에 해당하는 Appium 서버 URL 반환"""
    port = APPIUM_PORTS[key]
    return f"http://127.0.0.1:{port}"

# 테스트 대상 URL
BASE_URL = "https://ridibooks.com"

# 타임아웃 (초) 
TIMEOUT = {
    "implicit":    10,
    "explicit":    20,
    "page_load":   30,
    "new_command": 120,
}

# Android 디바이스 정보 
AOS_DEVICE = {
    # "real": {
    #     "device_name": "YOUR_AOS_DEVICE_NAME",
    #     "udid":        "YOUR_AOS_DEVICE_UDID",  # 실기기 필수 (adb devices 로 확인)
    # },
    "emulator": {
        "device_name": "emulator-5554",
        "udid":        "",  # 1개 실행 시 생략, 여러 대 실행 시 adb devices 로 확인 후 기재
    },
}

# # iOS 디바이스 정보
# IOS_DEVICE = {
#     "real": {
#         "device_name":      "YOUR_IOS_DEVICE_NAME",
#         "udid":             "YOUR_IOS_DEVICE_UDID",  # 실기기 필수 (Xcode > Devices 에서 확인)
#         "platform_version": "17.0",
#     },
#     "simulator": {
#         "device_name":      "iPhone 15",
#         "udid":             "",  # 1개 실행 시 생략, 여러 대 실행 시 xcrun simctl list 로 확인 후 기재
#         "platform_version": "17.0",
#     },
# }

# etc
CHROMEDRIVER_PATH = "/path/to/chromedriver"  # Samsung Browser용 chromedriver 경로

# 리포트 경로 (기기별 분리 + 타임스탬프) 
# 타임스탬프는 run_all.py 실행 시점에 생성해서 주입
# 직접 실행 시(pytest -m ...) 타임스탬프 없이 기기명만으로 저장
REPORT_DIR = "reports"

REPORT_NAMES = {
    "aos_emulator":  "report_aos_emulator",
    # "aos_real":      "report_aos_real",
    # "ios_simulator": "report_ios_simulator",
    # "ios_real":      "report_ios_real",
}

def get_report_path(key: str, timestamp: str = "") -> str:
    """
    기기별 리포트 경로 반환
    - run_all.py 실행 시: timestamp 주입 → report_aos_emulator_20240330_143022.html
    - 직접 실행 시: timestamp 없음 → report_aos_emulator.html
    """
    suffix = f"_{timestamp}" if timestamp else ""
    return f"{REPORT_DIR}/{REPORT_NAMES[key]}{suffix}.html"