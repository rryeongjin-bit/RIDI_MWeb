import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from config.settings import *

# 페이지 로드
def wait_for_page_load(driver, timeout=30):
    """페이지 로드 완료까지 대기 + 번역 팝업 자동 처리"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
def wait_for_url_change(driver, current_url, timeout=30):
    """현재 URL에서 벗어날 때까지 대기"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.current_url != current_url
    )

def wait_for_url_contains(driver, expected_url, timeout=30):
    """특정 URL이 포함될 때까지 대기"""
    WebDriverWait(driver, timeout).until(
        lambda d: expected_url in d.current_url
    )

# 플랫폼 판별
def get_platform(driver):
    """현재 driver의 플랫폼 반환 (android | ios)"""
    return driver.capabilities.get("platformName", "").lower()

def is_android(driver):
    return get_platform(driver) == "android"

def is_ios(driver):
    return get_platform(driver) == "ios"


#브러우저 판별
def get_browser(driver):
    """현재 실행 중인 브라우저 반환 (chrome | safari | samsung internet)"""
    return driver.capabilities.get("browserName", "").lower()


def is_chrome(driver):
    return "chrome" in get_browser(driver)


def is_safari(driver):
    return "safari" in get_browser(driver)


def is_samsung(driver):
    return "samsung" in get_browser(driver)


# 대기
def wait_for_element(driver, locator, timeout=20):
    """element 노출될 때까지 대기 후 반환"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )


def wait_for_element_visible(driver, locator, timeout=20):
    """element 화면에 보일 때까지 대기 후 반환"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_for_element_clickable(driver, locator, timeout=20):
    """element 클릭 가능할 때까지 대기 후 반환"""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )

def wait_for_url_not_contains(driver, url_part, timeout=30):
    """특정 문자열이 URL에서 사라질 때까지 대기"""
    WebDriverWait(driver, timeout).until(
        lambda d: url_part not in d.current_url
    )

def wait_seconds(seconds=1):
    """명시적 대기 (꼭 필요한 경우에만 사용)"""
    time.sleep(seconds)


# 스크롤
def scroll_down(driver, pixels=500):
    """화면 아래로 스크롤 (AOS/iOS 공통)"""
    driver.execute_script(f"window.scrollBy(0, {pixels});")


def scroll_up(driver, pixels=500):
    """화면 위로 스크롤 (AOS/iOS 공통)"""
    driver.execute_script(f"window.scrollBy(0, -{pixels});")


def scroll_to_element(driver, element):
    """특정 element 위치로 스크롤 (AOS/iOS 공통)"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def scroll_to_center_element(driver, element):
    """정중앙 위치로 스크롤 (AOS/iOS 공통)"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)


# 탭/클릭
def tap_element(driver, element):
    """
    element 탭/클릭
    - iOS Safari: click() 실패 시 JS click fallback
    - AOS: click() 시도 → 실패 시 JS click fallback
    """
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)

# 입력
def clear_and_input(driver, element, text):
    """
    입력창 초기화 후 텍스트 입력
    - iOS: clear() 후 send_keys가 안 되는 경우가 있어 JS로 value 초기화 후 입력
    - AOS: 일반 clear() + send_keys() 사용
    """
    if is_ios(driver):
        driver.execute_script("arguments[0].value = '';", element)
        element.send_keys(text)
    else:
        element.clear()
        element.send_keys(text)


# 키보드
def hide_keyboard(driver):
    """
    키보드 숨기기
    - iOS: 키보드 숨기기 미지원 케이스가 있어 예외 무시
    - AOS: hide_keyboard() 정상 동작
    """
    try:
        driver.hide_keyboard()
    except Exception:
        pass  # iOS에서 키보드가 이미 없는 경우 무시


# 스크린샷
def save_screenshot(driver, filename, device_key="unknown", timestamp=""):
    """
    스크린샷 저장 (기기별 + 타임스탬프 폴더 분리)
    저장 경로: screenshots/{device_key}/{timestamp}/{filename}
    예시: screenshots/aos_emulator/20240330_143022/test_login_PASS.png
    """
    from config.settings import SCREENSHOT_DIR
    folder = os.path.join(SCREENSHOT_DIR, device_key, timestamp) if timestamp \
        else os.path.join(SCREENSHOT_DIR, device_key)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    driver.save_screenshot(path)
    return path

# 시스템 팝업 처리
def dismiss_save_password_popup(driver):
    """
    비밀번호 저장 팝업 처리
    - iOS만 해당 (네이티브 시스템 팝업)
    - AOS는 해당 팝업 없으므로 skip
    """
    if is_android(driver):
        return

    try:
        switch_to_native(driver)
        not_now_btn = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//XCUIElementTypeButton[@name='Not Now']")
            )
        )
        not_now_btn.click()
    except Exception:
        pass
    finally:
        switch_to_webview(driver)

# 플랫폼별 처리방법 분리
def get_element_by_platform(driver, locator_aos, locator_ios):
    """
    플랫폼에 따라 다른 locator로 element 반환
    - AOS: locator_aos 사용
    - iOS: locator_ios 사용
    """
    locator = locator_aos if is_android(driver) else locator_ios
    return wait_for_element_clickable(driver, locator)


def close_browser(driver):
    """
    브라우저 종료
    - iOS Safari: 네이티브 컨텍스트로 전환 후 앱 종료
    - AOS: driver.quit()에서 자동 종료되므로 skip
    """
    if is_ios(driver):
        try:
            driver.execute_script("mobile: terminateApp", {"bundleId": "com.apple.mobilesafari"})
        except Exception:
            pass
        