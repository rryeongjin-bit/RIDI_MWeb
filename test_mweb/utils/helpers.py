# utils/helpers.py

import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 페이지 로드
def wait_for_page_load(driver, timeout=30):
    """페이지 로드 완료까지 대기 (document.readyState == complete)"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_url_change(driver, current_url, timeout=20):
    """현재 URL에서 벗어날 때까지 대기"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.current_url != current_url
    )


# 플랫폼 판별
def get_platform(driver):
    """현재 driver의 플랫폼 반환 (android | ios)"""
    return driver.capabilities.get("platformName", "").lower()


def is_android(driver):
    return get_platform(driver) == "android"


def is_ios(driver):
    return get_platform(driver) == "ios"


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


# 탭/클릭
def tap_element(driver, element):
    """
    element 탭/클릭
    - iOS Safari: 일반 click()이 간헐적으로 무시되는 경우가 있어 JS click으로 fallback
    - AOS: 일반 click() 사용
    """
    if is_ios(driver):
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
    else:
        element.click()


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
def save_screenshot(driver, filename, device_key="unknown"):
    """
    스크린샷 저장 (기기별 폴더 분리)
    저장 경로: screenshots/{device_key}/{filename}
    예시: screenshots/aos_emulator/test_login__fail.png
    """
    folder = os.path.join("screenshots", device_key)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    driver.save_screenshot(path)
    return path