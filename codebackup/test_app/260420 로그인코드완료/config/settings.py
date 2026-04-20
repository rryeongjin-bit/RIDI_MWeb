import os
from dotenv import load_dotenv

load_dotenv()

def _get_env(key: str) -> str:
    """
    환경 변수 로드 - 없을 경우 즉시 에러 발생
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"[settings] {key} 가 .env에 선언되지 않았습니다.")
    return value

# 앱 정보
APP_PACKAGE   = _get_env("APP_PACKAGE")
APP_ACTIVITY  = _get_env("APP_ACTIVITY")
BUNDLE_ID_AOS = _get_env("BUNDLE_ID_AOS")
BUNDLE_ID_IOS = _get_env("BUNDLE_ID_IOS")

# 테스트 계정
AOS_TEST_ID = _get_env("AOS_TEST_ID")
AOS_TEST_PW = _get_env("AOS_TEST_PW")
IOS_TEST_ID = _get_env("IOS_TEST_ID")
IOS_TEST_PW = _get_env("IOS_TEST_PW")

# Appium Server
APPIUM_HOST = os.getenv("APPIUM_HOST", "localhost")

# Timeout 기준값
DEFAULT_TIMEOUT = 10  
NETWORK_TIMEOUT = 30   
LONG_TIMEOUT    = 60   

# 산출물 저장 경로
REPORT_DIR     = "reports"
SCREENSHOT_DIR = "screenshots"
LOG_DIR        = "logs"