import os
import logging
import pytest
import subprocess
from datetime import datetime
from appium import webdriver
from selenium.webdriver.common.options import ArgOptions
from config.capabilities import  *
from config.settings import *
from utils.helpers import *
from tests.elements import *


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


#-m 옵션 파싱 → Capabilities 선택
def _get_caps_from_marker_expr(marker_expr: str):
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

    # call 단계에서 로그만 기록 (스크린샷은 모듈 완료 후)
    if call.when != "call":
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    logger    = getattr(driver, "_logger", None)
    test_name = item.nodeid.replace("/", "_").replace("::", "__")

    if logger:
        if report.passed:
            logger.info(f"PASS | {test_name}")
        elif report.failed:
            logger.error(f"FAIL | {test_name}")
            logger.error(f"에러: {report.longreprtext if hasattr(report, 'longreprtext') else 'N/A'}")


# driver fixture (scope=module) 
@pytest.fixture(scope="module")
def driver(request, session_timestamp):
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
    _driver._logger.info(f"모듈 테스트 시작: {request.node.name}")

    # AOS Chrome 번역 팝업 비활성화 
    if is_android(_driver):
        try:
            _driver.execute_script(
                "chrome.send('setGlobalizedStrings', [{}])"
            )
        except Exception:
            pass

        try:
            subprocess.run([
                "adb", "shell",
                "am", "broadcast",
                "-a", "com.android.chrome.intent.action.DISABLE_TRANSLATE",
            ], capture_output=True)
        except Exception:
            pass

    yield _driver

    # 모듈 전체 완료 후 스크린샷 저장 + 브라우저 종료 
    try:
        filename = f"{request.node.name}_{session_timestamp}_FINAL.png"
        path = save_screenshot(_driver, filename, device_key, session_timestamp)
        _driver._logger.info(f"최종 스크린샷 저장: {path}")
        print(f"\n📸 최종 스크린샷 저장: {path}")
    except Exception as e:
        print(f"\n⚠️ 스크린샷 저장 실패: {e}")

    close_browser(_driver)
    _driver.quit()


# 로그인 fixture 
@pytest.fixture(scope="module")
def logged_in(driver):
    """
    로그인 상태 fixture
    - scope="module"로 모듈 내 모든 테스트에서 로그인 상태 공유
    - driver fixture에 의존
    """
    login_data = LoginData.valid_aos if is_android(driver) else LoginData.valid_ios

    driver.get(URLs.LOGIN)
    wait_for_page_load(driver)

    id_input  = wait_for_element_clickable(driver, LoginPage.ID_INPUT)
    pw_input  = wait_for_element_clickable(driver, LoginPage.PW_INPUT)
    login_btn = wait_for_element_clickable(driver, LoginPage.LOGIN_BTN)

    tap_element(driver, id_input)
    clear_and_input(driver, id_input, login_data['id'])

    tap_element(driver, pw_input)
    clear_and_input(driver, pw_input, login_data['pw'])

    tap_element(driver, login_btn)
    dismiss_save_password_popup(driver)

    # 콜백 URL까지 완전히 벗어날 때까지 대기 (iOS 콜백 처리 고려)
    wait_for_url_not_contains(driver, "account/login")
    wait_for_page_load(driver)

    assert "account/login" not in driver.current_url, \
        f"로그인 실패. 현재 URL: {driver.current_url}"

    yield driver  # 로그인된 driver 반환