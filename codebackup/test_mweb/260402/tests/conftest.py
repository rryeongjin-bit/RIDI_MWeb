import os
import logging
import pytest
from datetime import datetime
from appium import webdriver
from selenium.webdriver.common.options import ArgOptions
from config.capabilities import  *
from config.settings import *
from utils.helpers import *


"""함수별 단독실행 구조
각 함수별 테스트의존성없으므로 클래스별로 order 순서 재지정필요함"""

# CLI 옵션 등록 
def pytest_addoption(parser):
    parser.addoption(
        "--device-key", action="store", default="",
        help="기기 키 (예: aos_emulator, ios_simulator)"
    )


# 마커에서 device_key 자동 추출 
def _extract_device_key_from_marker_expr(marker_expr: str) -> str:
    platform = None
    env      = None
    expr     = marker_expr.lower()

    for p in ("aos", "ios"):
        if p in expr:
            platform = p
            break

    for e in ("emulator", "simulator", "real"):
        if e in expr:
            env = e
            break

    if platform and env:
        return f"{platform}_{env}"
    return "unknown"


# -m 옵션 파싱 → Capabilities 선택
def _get_caps_from_marker_expr(marker_expr: str):
    """
    -m 옵션 문자열을 직접 파싱해서 CAPS_MAP에서 Capabilities 반환
    iter_markers() 역순 읽기 문제 완전 해결
    예) "aos and emulator and chrome" → ('aos', 'emulator', 'chrome')
    """
    platform = None
    env      = None
    browser  = None
    expr     = marker_expr.lower()

    for p in ("aos", "ios"):
        if p in expr:
            platform = p
            break

    for e in ("emulator", "simulator", "real"):
        if e in expr:
            env = e
            break

    for b in ("chrome", "samsung", "safari"):
        if b in expr:
            browser = b
            break

    key  = (platform, env, browser)
    caps = CAPS_MAP.get(key)

    if caps is None:
        raise ValueError(
            f"CAPS_MAP에 해당하는 Capabilities 없음 → {key}\n"
            f"지원 목록: {list(CAPS_MAP.keys())}"
        )
    return caps


# 리포트 자동 생성
def pytest_configure(config):
    if hasattr(config.option, "htmlpath") and config.option.htmlpath:
        return

    device_key = config.getoption("--device-key", default="", skip=True)
    if not device_key:
        marker_expr = config.getoption("-m", default="", skip=True)
        device_key  = _extract_device_key_from_marker_expr(marker_expr)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(REPORT_DIR, exist_ok=True)
    config.option.htmlpath = f"{REPORT_DIR}/report_{device_key}_{timestamp}.html"
    config.option.self_contained_html = True


# 기기 키 추출 
def _get_device_key_from_markers(markers):
    platform = None
    env      = None

    for marker in markers:
        if marker.name in ("aos", "ios"):
            platform = marker.name
        if marker.name in ("real", "emulator", "simulator"):
            env = marker.name

    if platform and env:
        return f"{platform}_{env}"
    return "unknown"


# 로거 설정 
def _setup_logger(device_key: str, timestamp: str) -> logging.Logger:
    log_folder = os.path.join(LOG_DIR, device_key)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, f"test_{timestamp}.log")

    logger = logging.getLogger(f"{device_key}_{timestamp}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)

    return logger


# Session 범위 타임스탬프
@pytest.fixture(scope="session")
def session_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# 테스트 결과 수집
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


# driver fixture 
@pytest.fixture(scope="function")
def driver(request, session_timestamp):
    # -m 옵션 문자열 직접 파싱
    marker_expr = request.config.getoption("-m", default="", skip=True)
    caps        = _get_caps_from_marker_expr(marker_expr).copy()
    server_url  = caps.pop("appium:serverUrl")

    options = ArgOptions()
    options.capabilities.update(caps)

    _driver = webdriver.Remote(server_url, options=options)
    _driver.implicitly_wait(TIMEOUT["implicit"])

    device_key          = _extract_device_key_from_marker_expr(marker_expr)
    _driver._device_key = device_key
    _driver._timestamp  = session_timestamp
    _driver._logger     = _setup_logger(device_key, session_timestamp)
    _driver._logger.info(f"테스트 시작: {request.node.nodeid}")

    yield _driver

    # 세션 종료 전 스크린샷 + 로그 처리 
    rep       = getattr(request.node, "rep_call", None)
    test_name = request.node.nodeid.replace("/", "_").replace("::", "__")

    if rep is not None:
        try:
            if rep.passed:
                filename = f"{test_name}_PASS.png"
                path = save_screenshot(_driver, filename, device_key, session_timestamp)
                _driver._logger.info(f"PASS | {test_name}")
                _driver._logger.info(f"스크린샷 저장: {path}")
                print(f"\n📸 성공 스크린샷 저장: {path}")

            elif rep.failed:
                filename = f"{test_name}_FAIL.png"
                path = save_screenshot(_driver, filename, device_key, session_timestamp)
                _driver._logger.error(f"FAIL | {test_name}")
                _driver._logger.error(f"스크린샷 저장: {path}")
                print(f"\n📸 실패 스크린샷 저장: {path}")

        except Exception as e:
            print(f"\n⚠️ 스크린샷 저장 실패: {e}")

    # 스크린샷 처리 후
    close_browser(_driver)  # iOS Safari 종료
    _driver.quit()