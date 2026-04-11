import time
import base64
import numpy as np
import cv2

"""     스크롤 시작전 이미지 스샷
    시작전 이미지 스샷의 마지막지점이 기기 최상단 도달시 스크롤중단
    -> 시작전/종료후 이미지 스샷의 차이로 이동거리 측정해서 속도계산 
    
    폴링방식 
    허용오차범위 3px/s를 커버하지 못하는 단점 발생"""
# ============================================================
# 공통 설정값
# ============================================================
CONFIGURED_PX_PER_SEC = 175    # 설계값 (물리px/s)
THRESHOLD_PX_PER_SEC  = 3.0    # 허용 오차 (물리px 기준)
POLL_INTERVAL         = 0.3    # 폴링 간격 (초)
MATCH_THRESHOLD       = 0.3    # 템플릿 매칭 신뢰도 기준
TOP_ARRIVAL_Y         = 0.15   # 화면 상단 몇 % 이내를 "최상단 도달"로 판단

APPIUM_SERVER = "http://127.0.0.1:4723"

# ============================================================
# 스크린샷 캡처 (adb screencap)
# 에뮬레이터 → 논리px / 실기기 → 물리px
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
# DPR 조회 (에뮬레이터 리사이즈용)
# ============================================================
def get_dpr(driver):
    info    = driver.execute_script("mobile: deviceInfo")
    density = info.get("displayDensity", 160)
    dpr     = density / 160
    print(f"[DPR] density: {density} → DPR: {dpr}")
    return dpr

# ============================================================
# 자동스크롤 속도 측정 (에뮬레이터/실기기 공통)
#
# is_emulator=True  → screencap(논리px) × DPR → 물리px 리사이즈
# is_emulator=False → screencap = 이미 물리px → 그대로 사용
# ============================================================
def measure_auto_scroll_speed(driver, is_emulator):

    print("\n콘텐츠 화면 준비 후 엔터를 눌러주세요...")
    input()

    # ── before 스크린샷 캡처 ────────────────────────────────
    img_before = capture_screenshot(driver)

    if is_emulator:
        dpr    = get_dpr(driver)
        phys_w = int(img_before.shape[1] * dpr)
        phys_h = int(img_before.shape[0] * dpr)
        img_before = cv2.resize(img_before, (phys_w, phys_h))
        print(f"[에뮬레이터] 논리px → 물리px 리사이즈: {phys_w} × {phys_h}")
    else:
        phys_h = img_before.shape[0]  # 이미 물리px
        phys_w = img_before.shape[1]
        print(f"[실기기] 물리px: {phys_w} × {phys_h}")

    cv2.imwrite("before.png", img_before)

    # ── 하단 템플릿 추출 ────────────────────────────────────
    h, w      = img_before.shape[:2]
    tmpl_y1   = int(h * 0.88)
    tmpl_y2   = int(h * 0.98)
    template  = img_before[tmpl_y1:tmpl_y2, :]
    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    print(f"[템플릿] 하단 구간 y={tmpl_y1}~{tmpl_y2}px 추출")
    print("─" * 50)
    print("지금 자동스크롤을 시작하세요!")
    print("before 하단 콘텐츠가 화면 최상단에 도달하면 자동 종료됩니다.")
    print("─" * 50)

    # ── 폴링: 스크롤 시작 감지 → 최상단 도달 감지 ──────────
    t_scroll_start = None
    t_arrived      = None
    img_after      = None
    start_y        = None
    prev_y         = tmpl_y1

    while True:
        time.sleep(POLL_INTERVAL)
        curr_img = capture_screenshot(driver)

        if is_emulator:
            curr_img = cv2.resize(curr_img, (phys_w, phys_h))

        gray_curr              = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)
        result                 = cv2.matchTemplate(gray_curr, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        matched_y              = max_loc[1]

        # 스크롤 시작 감지 (템플릿이 실제로 움직이기 시작한 시점)
        if t_scroll_start is None and abs(matched_y - prev_y) > 50:
            t_scroll_start = time.time()
            start_y        = prev_y
            print(f"  ▶ 스크롤 시작 감지! y={start_y}px")

        print(f"  [폴링] 신뢰도={max_val:.3f}  y={matched_y}px  (목표 y≤{int(h * TOP_ARRIVAL_Y)}px)")

        # 최상단 도달 감지
        if t_scroll_start and max_val >= MATCH_THRESHOLD and matched_y <= int(h * TOP_ARRIVAL_Y):
            t_arrived = time.time()
            end_y     = matched_y
            img_after = curr_img
            print(f"\n  ✅ 하단 콘텐츠 최상단 도달! (y={end_y}px)")
            break

        prev_y = matched_y

    cv2.imwrite("after.png", img_after)

    # ── 결과 계산 ───────────────────────────────────────────
    actual_distance = start_y - end_y       # 실제 이동거리 (물리px)
    elapsed         = t_arrived - t_scroll_start
    speed_physical  = actual_distance / elapsed
    error_px        = abs(CONFIGURED_PX_PER_SEC - speed_physical)
    error_rate      = (error_px / CONFIGURED_PX_PER_SEC * 100)

    print(f"\n{'='*50}")
    print(f"[측정 결과]")
    print(f"{'='*50}")
    print(f"이동 거리 (물리px)       : {actual_distance}px  ({start_y} → {end_y})")
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