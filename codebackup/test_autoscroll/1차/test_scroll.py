import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

""" 특정시간동안 자동스크롤을 1.0배속으로 진행했을때의 평균 속도값측정 방법 2"""

# 설정값 
PLATFORM              = "android"  # "android" or "ios"
IS_EMULATOR           = True
CONFIGURED_PX_PER_SEC = 175
MEASURE_DURATION      = 10         # 측정 시간 (초)
THRESHOLD_PX_PER_SEC  = 3.0        # 허용 오차 (물리px 기준)

APPIUM_SERVER = "http://127.0.0.1:4723"

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
        "platformName":  "iOS",
        "bundleId":      "com.your.app",
        "noReset":       True,
        "automationName":"XCUITest",
    }
    if IS_EMULATOR:
        caps["deviceName"] = "iPhone 15 Pro"
        caps["udid"]       = "your-simulator-uuid"
    else:
        caps["deviceName"] = "your_device_name"
        caps["udid"]       = "your-real-device-udid"
    options.load_capabilities(caps)
    return options

# DPR 조회
def get_dpr(driver):
    info    = driver.execute_script("mobile: deviceInfo")
    density = info.get("displayDensity", 160)
    dpr     = density / 160
    print(f"[DPR] density: {density} → DPR: {dpr}")
    return dpr

# 스크롤 위치 조회 - adb shell 방식 
def get_scroll_position(driver):
    if PLATFORM == "android":
        # adb shell로 reader_view의 scrollY 직접 조회
        result = driver.execute_script(
            "mobile: shell",
            {"command": "dumpsys", "args": ["window", "windows"]}
        )
        # scrollY 파싱 시도
        for line in result.splitlines():
            if "reader_view" in line and "scrollY" in line:
                try:
                    idx = line.index("scrollY=")
                    val = line[idx+8:].split()[0].rstrip(",)")
                    return float(val)
                except (ValueError, IndexError):
                    pass

        # fallback: view 위치로 추정
        result2 = driver.execute_script(
            "mobile: shell",
            {"command": "dumpsys", "args": ["activity", "top"]}
        )
        for line in result2.splitlines():
            if "reader_view" in line:
                try:
                    idx = line.index("scrollY=")
                    val = line[idx+8:].split()[0].rstrip(",)")
                    return float(val)
                except (ValueError, IndexError):
                    pass
        return 0.0

    elif PLATFORM == "ios":
        scroll_el = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeScrollView")
        return float(scroll_el.location["y"])

# 자동스크롤 속도 측정
def measure_auto_scroll_speed(driver):
    dpr = get_dpr(driver)

    print(f"\n{'='*50}")
    print(f"자동스크롤 속도 측정 시작")
    print(f"측정 시간: {MEASURE_DURATION}초")
    print(f"설계 목표값: {CONFIGURED_PX_PER_SEC} CSS px/s")
    print(f"{'='*50}\n")

    samples    = []
    start_time = time.time()

    while time.time() - start_time < MEASURE_DURATION:
        t   = time.time()
        pos = get_scroll_position(driver)
        samples.append({"time": t, "logical_px": pos, "physical_px": pos * dpr})
        print(f"  [샘플] t={t - start_time:.2f}s  scrollY={pos:.1f}px")

    print(f"\n[측정] 수집된 샘플 수: {len(samples)}")

    if len(samples) < 2:
        print("❌ 샘플 부족. 자동스크롤이 동작 중인지 확인하세요.")
        return

    # 속도 계산
    frame_speeds_logical  = []
    frame_speeds_physical = []

    for i in range(1, len(samples)):
        d_logical  = samples[i]["logical_px"]  - samples[i-1]["logical_px"]
        d_physical = samples[i]["physical_px"] - samples[i-1]["physical_px"]
        d_t        = samples[i]["time"]        - samples[i-1]["time"]
        if d_t > 0:
            frame_speeds_logical.append(abs(d_logical  / d_t))
            frame_speeds_physical.append(abs(d_physical / d_t))

    avg_logical   = sum(frame_speeds_logical)  / len(frame_speeds_logical)
    avg_physical  = sum(frame_speeds_physical) / len(frame_speeds_physical)
    last_logical  = frame_speeds_logical[-1]
    last_physical = frame_speeds_physical[-1]

    conf_physical = CONFIGURED_PX_PER_SEC * dpr
    error_px      = abs(conf_physical - avg_physical)
    error_rate    = (error_px / conf_physical * 100) if conf_physical else 0

    # 결과 출력
    print(f"\n{'='*50}")
    print(f"[측정 결과]")
    print(f"{'='*50}")
    print(f"configuredPxPerSec      : {CONFIGURED_PX_PER_SEC} (CSS px)")
    print(f"configuredPhysPxPerSec  : {conf_physical:.1f} (물리px)")
    print(f"avgMeasuredPxPerSec     : {avg_logical:.1f} (CSS px/s)")
    print(f"avgMeasuredPhysPxPerSec : {avg_physical:.1f} (물리px/s)")
    print(f"lastFramePxPerSec       : {last_logical:.1f} (CSS px/s)")
    print(f"lastFramePhysPxPerSec   : {last_physical:.1f} (물리px/s)")
    print(f"DPR                     : {dpr}")
    print(f"{'='*50}")
    print(f"오차 (물리px)           : {error_px:.1f} px/s")
    print(f"오차율                  : {error_rate:.1f}%")
    print(f"{'='*50}")

    result = "✅ PASS" if error_px <= THRESHOLD_PX_PER_SEC else "❌ FAIL"
    print(f"판정 (허용오차 {THRESHOLD_PX_PER_SEC}px/s) : {result}")
    print(f"{'='*50}\n")

# 실행
def test_auto_scroll_speed():
    if PLATFORM == "android":
        driver = webdriver.Remote(APPIUM_SERVER, options=get_android_caps())
    else:
        driver = webdriver.Remote(APPIUM_SERVER, options=get_ios_caps())

    try:
        info = driver.execute_script("mobile: deviceInfo")
        size = driver.get_window_size()
        dpr  = info.get("displayDensity", 160) / 160
        print(f"[해상도] 논리px: {size['width']} × {size['height']}")
        print(f"[해상도] 물리px: {size['width']*dpr:.0f} × {size['height']*dpr:.0f}")
        print(f"[해상도] DPR: {dpr}")

        print(f"\n자동스크롤을 시작하세요. 5초 후 측정 시작합니다...")
        time.sleep(5)

        measure_auto_scroll_speed(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auto_scroll_speed()