import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.settings import *


class BasePage:
    def __init__(self, driver, platform: str):
        self.driver   = driver
        self.platform = platform
        self.log      = logging.getLogger(__name__)

    # 요소 탐색
    def find_element(self, locator: tuple):
        try:
            return self.driver.find_element(*locator)
        except NoSuchElementException as e:
            self.log.error(f"[find_element] 요소 없음: {locator} | {e}")
            raise

    def find_elements(self, locator: tuple):
        return self.driver.find_elements(*locator)

    # 대기
    def wait_for_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element] 타임아웃: {locator} | {timeout}s")
            raise

    def wait_for_element_visible(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element_visible] 타임아웃: {locator} | {timeout}s")
            raise

    def wait_for_element_clickable(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            self.log.error(f"[wait_for_element_clickable] 타임아웃: {locator} | {timeout}s")
            raise

    # 액션
    def click(self, locator: tuple):
        el = self.wait_for_element_clickable(locator)
        el.click()
        self.log.info(f"[click] {locator}")

    def send_keys(self, locator: tuple, value: str):
        el = self.wait_for_element_visible(locator)
        el.clear()
        el.send_keys(value)
        self.log.info(f"[send_keys] {locator} | value: {value}")

    def get_text(self, locator: tuple) -> str:
        el = self.wait_for_element_visible(locator)
        return el.text

    def is_displayed(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT) -> bool:
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False
    
    def is_present(self, locator: tuple, timeout: int = 2) -> bool:
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    
    # 스크롤
    def scroll_down(self):
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.8)
        end_y   = int(size["height"] * 0.2)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration=800)
        self.log.info("[scroll_down]")

    def scroll_up(self):
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.2)
        end_y   = int(size["height"] * 0.8)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration=800)
        self.log.info("[scroll_up]")

    # 네이티브 <-> WebView 전환
    def switch_to_webview(self, timeout: int = NETWORK_TIMEOUT):
        """
        WebView 컨텍스트로 전환
        WebView가 여러 개일 경우 마지막 WebView로 전환
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len([
                    ctx for ctx in d.contexts
                    if "WEBVIEW" in ctx
                ]) > 0
            )
            contexts = self.driver.contexts
            webviews = [ctx for ctx in contexts if "WEBVIEW" in ctx]

            if not webviews:
                raise RuntimeError("[switch_to_webview] WebView 컨텍스트 없음")

            # 마지막 WebView로 전환 (동적 WebView 대응)
            target = webviews[-1]
            self.driver.switch_to.context(target)
            self.log.info(f"[switch_to_webview] 전환 완료: {target}")

        except TimeoutException:
            self.log.error("[switch_to_webview] WebView 전환 타임아웃")
            raise

    def switch_to_native(self):
        """네이티브 컨텍스트로 전환"""
        self.driver.switch_to.context("NATIVE_APP")
        self.log.info("[switch_to_native] 네이티브 전환 완료")

    def switch_to_webview_by_index(self, index: int = 0):
        """
        특정 인덱스의 WebView로 전환
        WebView가 여러 개일 때 특정 WebView 지정 필요 시 사용
        """
        contexts = self.driver.contexts
        webviews = [ctx for ctx in contexts if "WEBVIEW" in ctx]

        if index >= len(webviews):
            raise IndexError(f"[switch_to_webview_by_index] 인덱스 초과: {index} / 전체: {len(webviews)}")

        target = webviews[index]
        self.driver.switch_to.context(target)
        self.log.info(f"[switch_to_webview_by_index] 전환 완료: {target}")

    def get_current_context(self) -> str:
        """현재 컨텍스트 반환"""
        return self.driver.current_context