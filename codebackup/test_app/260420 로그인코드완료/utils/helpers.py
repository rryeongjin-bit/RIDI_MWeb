import os
import logging
from datetime import datetime
from config.settings import *

log = logging.getLogger(__name__)

# 타임스탬프
def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# 경로 생성
def get_screenshot_path(platform: str, test_name: str) -> str:
    """스크린샷 저장 경로 생성"""
    ts  = get_timestamp()
    dir = os.path.join(SCREENSHOT_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{ts}_{test_name}.png")


def get_log_path(platform: str, timestamp: str) -> str:
    """로그 저장 경로 생성"""
    dir = os.path.join(LOG_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{timestamp}_{platform}.log")


def get_report_path(platform: str, timestamp: str) -> str:
    """리포트 저장 경로 생성"""
    dir = os.path.join(REPORT_DIR, platform)
    os.makedirs(dir, exist_ok=True)
    return os.path.join(dir, f"{timestamp}_{platform}_report.html")

# 디렉토리 초기화
def init_output_dirs(platform: str):
    """산출물 디렉토리 초기화 (없으면 생성)"""
    dirs = [
        os.path.join(SCREENSHOT_DIR, platform),
        os.path.join(LOG_DIR, platform),
        os.path.join(REPORT_DIR, platform),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        log.info(f"[init_output_dirs] 디렉토리 확인: {d}")