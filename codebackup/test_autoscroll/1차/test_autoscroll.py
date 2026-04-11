
import time
import base64
import numpy as np
import cv2
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions


""" 기기해상도 물리 px 기준으로 기기 최상단부터 최하단까지 1.0 배속으로 스크롤할떄의 실제 속도값 (px/s) """
# 기존 Appium 서버 종료 후 아래 명령어로 재시작해야함
# appium --allow-insecure adb_shell

# ============================================================
# 설정값
# ============================================================
PLATFORM              = "android"
IS_EMULATOR           = True
CONFIGURED_PX_PER_SEC = 175    # 설계값 (물리px/s)
THRESHOLD_PX_PER_SEC  = 3.0    # 허용 오차 (물리px 기준)
POLL_INTERVAL         = 0.3    # 폴링 간격 (초) - 짧을수록 정확
MATCH_THRESHOLD       = 0.3    # 캔버스 기반 콘텐츠라 낮게 설정
TOP_ARRIVAL_Y         = 0.15   # 화면 상단 몇 % 이내를 "최상단 도달"로 판단

APPIUM_SERVER = "http://127.0.0.1:4723"

# ============================================================
# Capabilities
# ============================================================
def get_android_caps():
    options = UiAutomator2Options()
    caps = {
        "platformName": "Android",
        "appPackage":  "com.initialcoms.ridi.staging",  
        "appActivity": "com.ridi.books.viewer.main.activity.SplashActivity",
        "noReset": True,
        "automationName": "UiAutomator2"
    }
    caps["deviceName"] = "emulator-5554" if IS_EMULATOR else "galaxy s25"
    options.load_capabilities(caps)
    return options

def get_ios_caps():
    options = XCUITestOptions()
    caps = {
        "platformName":   "iOS",
        "bundleId":       "com.your.app",
        "noReset":        True,
        "automationName": "XCUITest",
    }
    if IS_EMULATOR:
        caps["deviceName"] = "iPhone 15 Pro"
        caps["udid"]       = "your-simulator-uuid"
    else:
        caps["deviceName"] = "your_device_name"
        caps["udid"]       = "your-real-device-udid"
    options.load_capabilities(caps)
    return options

# ============================================================
# 스크린샷 캡처 (adb screencap → 물리px 기준)
# ============================================================
def capture_screenshot(driver):
    driver.execute_script("mobile: shell", {
        "command": "screencap",
        "args": ["-p", "/sdcard/sc.png"]
    })
    data      = driver.pull_file("/sdcard/sc.png")
    img_bytes = base64.b64decode(data)
    arr       = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

# ============================================================
# 측정 메인
# 원리:
#   before 스샷 하단 콘텐츠를 템플릿으로 추출
#   → 자동스크롤 중 해당 콘텐츠가 화면 최상단에 도달하는 시점 감지
#   → 이동거리 = 화면 물리 높이 (고정값)
#   → 속도 = 화면높이 ÷ elapsed
# ============================================================
def measure_auto_scroll_speed(driver):

    # 화면 물리 높이 → screencap 이미지에서 직접 조회
    img_before = capture_screenshot(driver)
    t_before   = time.time()
    phys_h     = img_before.shape[0]  # adb screencap = 물리px
    phys_w     = img_before.shape[1]

    print(f"[해상도] 물리px: {phys_w} × {phys_h}")
    print(f"[이동거리] 화면 높이 고정값: {phys_h} 물리px\n")

    # ── Step 2: 하단 템플릿 추출 ────────────────────────────
    # before 스샷 하단 10% 구간을 템플릿으로 사용
    h, w       = img_before.shape[:2]
    tmpl_y1    = int(h * 0.88)
    tmpl_y2    = int(h * 0.98)
    template   = img_before[tmpl_y1:tmpl_y2, :]
    gray_tmpl  = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    print(f"  [템플릿] 하단 구간 y={tmpl_y1}~{tmpl_y2}px 추출\n")
    print("─" * 50)
    print("지금 자동스크롤을 시작하세요!")
    print("before 하단 콘텐츠가 화면 최상단에 도달하면 자동 종료됩니다.")
    print("─" * 50)

    # ── Step 3: 템플릿이 화면 최상단에 도달하는 시점 감지 ──
    t_arrived  = None
    img_after  = None

    while True:
        time.sleep(POLL_INTERVAL)
        curr_img  = capture_screenshot(driver)
        gray_curr = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)

        result               = cv2.matchTemplate(gray_curr, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        matched_y            = max_loc[1]

        print(f"  [폴링] 매칭 신뢰도={max_val:.3f}  현재 위치 y={matched_y}px")

        # 템플릿이 화면 상단 10% 이내에 도달했을 때 종료
        if max_val >= MATCH_THRESHOLD and matched_y <= int(h * 0.1):
            t_arrived = time.time()
            img_after = curr_img
            print(f"\n  ✅ 하단 콘텐츠가 최상단 도달! (y={matched_y}px)")
            break

    # ── Step 4: 결과 계산 ────────────────────────────────────
    cv2.imwrite("after.png", img_after)

    elapsed        = t_arrived - t_before
    speed_physical = phys_h / elapsed
    error_px       = abs(CONFIGURED_PX_PER_SEC - speed_physical)
    error_rate     = (error_px / CONFIGURED_PX_PER_SEC * 100)

    print(f"\n{'='*50}")
    print(f"[측정 결과]")
    print(f"{'='*50}")
    print(f"이동 거리 (물리px)       : {phys_h}px (화면 높이 고정)")
    print(f"실제 소요 시간           : {elapsed:.2f}초")
    print(f"configuredPxPerSec      : {CONFIGURED_PX_PER_SEC} (물리px/s)")
    print(f"measuredPhysPxPerSec    : {speed_physical:.1f} (물리px/s)")
    print(f"{'='*50}")
    print(f"오차 (물리px)           : {error_px:.1f} px/s")
    print(f"오차율                  : {error_rate:.1f}%")
    print(f"{'='*50}")
    result_str = "✅ PASS" if error_px <= THRESHOLD_PX_PER_SEC else "❌ FAIL"
    print(f"판정 (허용오차 {THRESHOLD_PX_PER_SEC}px/s) : {result_str}")
    print(f"{'='*50}\n")

# ============================================================
# 실행
# ============================================================
def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())

    try:
        measure_auto_scroll_speed(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()