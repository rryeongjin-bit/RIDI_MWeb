
import pytest
from appium import webdriver
from selenium.webdriver.common.options import ArgOptions
from config.capabilities import CAPS_MAP
from config.settings import TIMEOUT
from utils.helpers import save_screenshot


# 마커 → Capabilities 선택 
def _get_caps_from_markers(markers):
    """
    테스트 함수에 붙은 마커를 읽어 CAPS_MAP에서 해당 Capabilities 반환
    마커 조합: (플랫폼, 환경, 브라우저)
    """
    platform = None
    env      = None
    browser  = None

    for marker in markers:
        if marker.name in ("aos"):
            platform = marker.name
        if marker.name in ("emulator"):
            env = marker.name
        if marker.name in ("chrome"):
            browser = marker.name
        # if marker.name in ("aos", "ios"):
        #     platform = marker.name
        # if marker.name in ("real", "emulator", "simulator"):
        #     env = marker.name
        # if marker.name in ("chrome", "samsung", "safari"):
        #     browser = marker.name

    key = (platform, env, browser)
    caps = CAPS_MAP.get(key)

    if caps is None:
        raise ValueError(
            f"CAPS_MAP에 해당하는 Capabilities 없음 → {key}\n"
            f"지원 목록: {list(CAPS_MAP.keys())}"
        )
    return caps


def _get_device_key_from_markers(markers):
    """스크린샷 폴더 구분을 위한 기기 키 반환 (예: aos_emulator)"""
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


# driver fixture 
@pytest.fixture(scope="function")
def driver(request):
    caps = _get_caps_from_markers(request.node.iter_markers()).copy()
    server_url = caps.pop("appium:serverUrl")

    options = ArgOptions()
    options.capabilities.update(caps)

    _driver = webdriver.Remote(server_url, options=options)
    _driver.implicitly_wait(TIMEOUT["implicit"])

    # 기기 키를 driver에 임시 저장 (스크린샷 경로 분리용)
    _driver._device_key = _get_device_key_from_markers(request.node.iter_markers())

    yield _driver

    _driver.quit()


# 실패 시 스크린샷 자동 저장
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def capture_on_failure(request):
    yield
    driver = request.node.funcargs.get("driver")  # driver 없는 테스트면 None 반환
    if driver is None:
        return
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        test_name = request.node.nodeid.replace("/", "_").replace("::", "__")
        device_key = getattr(driver, "_device_key", "unknown")
        path = save_screenshot(driver, f"{test_name}.png", device_key)
        print(f"\n📸 실패 스크린샷 저장: {path}")