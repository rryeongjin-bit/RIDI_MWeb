import time
import base64
import subprocess
import numpy as np
import cv2
import os
from datetime import datetime

""" 설계값과 실측값을 비교, 오차/오차율 출력
[실측값]
물리 화면 높이 = 2400px
소요 시간      = 13초

실측 속도 = 2400 ÷ 13 = 184.6 물리px/s

[설계값과 비교]
설계값   : 175 물리px/s
실측값   : 184.6 물리px/s

오차     : 184.6 - 175 = 9.6 px/s
오차율   : 9.6 ÷ 175 × 100 = 5.5%

[애뮬레이터/실기기 스냅샷]
screencap이 논리px면?
→ 물리px로 변환 필요 (× DPR)

screencap이 물리px면?
→ 그대로 사용

에뮬레이터 screencap → 논리px (1080 × 2400)
실기기 screencap     → 물리px (2835 × 6300)
=> 애뮬레이터의 실제 물리 px가 코드상에서 논리 px로 찍힘. 결론은 dpr고려안하고 애뮬레이터 논리 px = 실기기 물리 px에 해당함

[측정공식]
에뮬레이터:
  이동거리(물리px) = 이동거리(논리px) 
  속도 = 이동거리(물리px) ÷ 소요시간

실기기:
  속도 = 이동거리(물리px) ÷ 소요시간

비교:
  설계값 175 물리px/s vs 실측값
  오차 = |175 - 실측값|

[결과]
[화면] 1080 × 2400px
[템플릿] y=2112~2352px 추출
  [녹화] 시작됨
──────────────────────────────────────────────────
지금 자동스크롤을 시작하세요!
before 하단 콘텐츠가 최상단 도달 시 자동 종료됩니다.
──────────────────────────────────────────────────
  [감지] y=2112px  (목표 y≤360px)
  [감지] y=2112px  (목표 y≤360px)
  [감지] y=1872px  (목표 y≤360px)
  [감지] y=1661px  (목표 y≤360px)
  [감지] y=1445px  (목표 y≤360px)
  [감지] y=1244px  (목표 y≤360px)
  [감지] y=1046px  (목표 y≤360px)
  [감지] y=839px  (목표 y≤360px)
  [감지] y=641px  (목표 y≤360px)
  [감지] y=448px  (목표 y≤360px)
  [감지] y=280px  (목표 y≤360px)

  ✅ 최상단 도달! → 녹화 중지
/sdcard/scroll.mp4: 1 file pulled, 0 skipped. 193.4 MB/s (9525152 bytes in 0.047s)
  [녹화] 중지 및 scroll.mp4 저장됨

[프레임 분석] scroll.mp4 분석 중...
  [영상] fps=45.6
  [프레임] 총 573프레임 / 유효 573개
  ▶ 시작 프레임: 38 (y=2097px)
  ■ 종료 프레임: 532 (y=358px)

==================================================
항목                                      값
==================================================
스크롤 배속                               1.0x
설계값 (px/s)                            175
실측값 (px/s)                          160.5
소요 시간                              10.83초
화면 높이                               2400px
오차 (px/s)                            14.5
오차율                                  8.3%
==================================================
판정                                 ❌ FAIL
==================================================

  """

# ============================================================
# 공통 설정값
# ============================================================
CONFIGURED_PX_PER_SEC = 175    # 설계값 (px/s)
THRESHOLD_PX_PER_SEC  = 3.0    # 허용 오차 (px/s)
MATCH_THRESHOLD       = 0.3    # 템플릿 매칭 신뢰도 기준
TOP_ARRIVAL_Y         = 0.15   # 화면 상단 몇 % 이내를 "최상단 도달"로 판단
RECORD_DIR            = "recordings"  # 녹화 파일 저장 폴더

APPIUM_SERVER = "http://127.0.0.1:4723"

# ============================================================
# 저장 경로 생성
# ============================================================
def get_save_paths(platform, device_name, speed_label, ts):
    # 환경별 폴더 구조: recordings/android_emulator/ or ios_simulator/ etc.
    folder = os.path.join(RECORD_DIR, f"{platform}_{device_name}")
    os.makedirs(folder, exist_ok=True)

    base        = f"{speed_label}_{ts}"
    video_path  = os.path.join(folder, f"scroll_{base}.mp4")
    before_path = os.path.join(folder, f"before_{base}.png")
    after_path  = os.path.join(folder, f"after_{base}.png")
    return folder, video_path, before_path, after_path

# ============================================================
# 스크린샷 캡처
# Android: adb screencap / iOS: Appium screenshot
# ============================================================
def capture_screenshot(driver, platform="android"):
    if platform == "android":
        driver.execute_script("mobile: shell", {
            "command": "screencap",
            "args": ["-p", "/sdcard/sc.png"]
        })
        data      = driver.pull_file("/sdcard/sc.png")
        img_bytes = base64.b64decode(data)
        arr       = np.frombuffer(img_bytes, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        # iOS: Appium 내장 스크린샷 사용
        png = driver.get_screenshot_as_png()
        arr = np.frombuffer(png, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

# ============================================================
# 녹화 시작/중지
# Android: adb screenrecord / iOS: Appium start_recording_screen
# ============================================================
def start_recording(driver, platform="android"):
    if platform == "android":
        subprocess.run(["adb", "shell", "rm", "-f", "/sdcard/scroll.mp4"],
                       capture_output=True)
        proc = subprocess.Popen(
            ["adb", "shell", "screenrecord",
             "--bit-rate", "8000000",
             "/sdcard/scroll.mp4"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("  [녹화] Android 녹화 시작됨")
        return proc
    else:
        driver.start_recording_screen()
        print("  [녹화] iOS 녹화 시작됨")
        return None

def stop_recording(driver, proc, save_path, platform="android"):
    os.makedirs(RECORD_DIR, exist_ok=True)

    if platform == "android":
        proc.terminate()
        time.sleep(1.5)
        subprocess.run(["adb", "pull", "/sdcard/scroll.mp4", save_path])
    else:
        video_data = driver.stop_recording_screen()
        import base64 as b64
        with open(save_path, "wb") as f:
            f.write(b64.b64decode(video_data))

    print(f"  [녹화] 중지 및 저장됨 → {save_path}")

# ============================================================
# 프레임 분석
# ============================================================
def analyze_frames(template, screen_h, video_path):
    print(f"\n[프레임 분석] {video_path} 분석 중...")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"  [영상] fps={fps:.1f}")

    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    positions = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame             = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result                 = cv2.matchTemplate(gray_frame, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= MATCH_THRESHOLD:
            positions.append((frame_idx, max_loc[1]))
        frame_idx += 1

    cap.release()
    print(f"  [프레임] 총 {frame_idx}프레임 / 유효 {len(positions)}개")

    start_frame = end_frame = None
    start_y_val = end_y_val = None

    for i in range(1, len(positions)):
        prev_f, prev_y = positions[i-1]
        curr_f, curr_y = positions[i]

        if start_frame is None and (prev_y - curr_y) > 3:
            start_frame = prev_f
            start_y_val = prev_y
            print(f"  ▶ 시작 프레임: {start_frame} (y={start_y_val}px)")

        if start_frame and curr_y <= int(screen_h * TOP_ARRIVAL_Y):
            end_frame = curr_f
            end_y_val = curr_y
            print(f"  ■ 종료 프레임: {end_frame} (y={end_y_val}px)")
            break

    if start_frame is None or end_frame is None:
        return None

    elapsed  = (end_frame - start_frame) / fps
    distance = start_y_val - end_y_val
    speed    = distance / elapsed

    return {
        "elapsed":     elapsed,
        "distance":    distance,
        "speed":       speed,
        "fps":         fps,
        "start_frame": start_frame,
        "end_frame":   end_frame,
    }

# ============================================================
# 자동스크롤 속도 측정 메인
# ============================================================
def measure_auto_scroll_speed(driver, speed_label="1.0x", platform="android", device_name="device"):

    ts                          = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder, video_path, before_path, after_path = get_save_paths(platform, device_name, speed_label, ts)

    print("\n콘텐츠 화면 준비 후 엔터를 눌러주세요...")
    input()

    # ── before 스크린샷 ──────────────────────────────────────
    img_before = capture_screenshot(driver, platform)
    screen_h   = img_before.shape[0]
    screen_w   = img_before.shape[1]
    print(f"[화면] {screen_w} × {screen_h}px")

    os.makedirs(RECORD_DIR, exist_ok=True)
    cv2.imwrite(before_path, img_before)
    print(f"[before] {before_path} 저장됨")

    # ── 하단 템플릿 추출 ─────────────────────────────────────
    tmpl_y1   = int(screen_h * 0.88)
    tmpl_y2   = int(screen_h * 0.98)
    template  = img_before[tmpl_y1:tmpl_y2, :]
    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    print(f"[템플릿] y={tmpl_y1}~{tmpl_y2}px 추출")

    # ── 녹화 시작 ────────────────────────────────────────────
    rec_proc = start_recording(driver, platform)
    time.sleep(0.5)

    print("─" * 50)
    print("지금 자동스크롤을 시작하세요!")
    print("before 하단 콘텐츠가 최상단 도달 시 자동 종료됩니다.")
    print("─" * 50)

    # ── 최상단 도달 감지 ─────────────────────────────────────
    prev_y = tmpl_y1

    while True:
        time.sleep(0.3)
        curr_img  = capture_screenshot(driver, platform)
        gray_curr = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)
        result    = cv2.matchTemplate(gray_curr, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        matched_y = max_loc[1]

        print(f"  [감지] y={matched_y}px  (목표 y≤{int(screen_h * TOP_ARRIVAL_Y)}px)")

        if matched_y <= int(screen_h * TOP_ARRIVAL_Y) and matched_y < prev_y:
            print(f"\n  ✅ 최상단 도달! → 녹화 중지")
            cv2.imwrite(after_path, curr_img)
            print(f"[after] {after_path} 저장됨")
            break

        prev_y = matched_y

    stop_recording(driver, rec_proc, video_path, platform)

    # ── 프레임 분석 ──────────────────────────────────────────
    result = analyze_frames(template, screen_h, video_path)

    if result is None:
        print("❌ 스크롤 시작/종료 프레임 감지 실패")
        return

    # ── 결과 출력 ────────────────────────────────────────────
    speed    = result["speed"]
    elapsed  = result["elapsed"]
    error    = abs(CONFIGURED_PX_PER_SEC - speed)
    error_rt = (error / CONFIGURED_PX_PER_SEC * 100)
    verdict  = "✅ PASS" if error <= THRESHOLD_PX_PER_SEC else "❌ FAIL"

    print(f"\n{'='*50}")
    print(f"{'항목':<20} {'값':>20}")
    print(f"{'='*50}")
    print(f"{'스크롤 배속':<20} {speed_label:>20}")
    print(f"{'설계값 (px/s)':<20} {CONFIGURED_PX_PER_SEC:>20}")
    print(f"{'실측값 (px/s)':<20} {speed:>20.1f}")
    print(f"{'소요 시간':<20} {elapsed:>19.2f}초")
    print(f"{'화면 높이':<20} {screen_h:>19}px")
    print(f"{'오차 (px/s)':<20} {error:>20.1f}")
    print(f"{'오차율':<20} {error_rt:>19.1f}%")
    print(f"{'='*50}")
    print(f"{'판정':<20} {verdict:>20}")
    print(f"{'='*50}")
    print(f"\n[저장 폴더] {folder}")
    print(f"  before  → {os.path.basename(before_path)}")
    print(f"  after   → {os.path.basename(after_path)}")
    print(f"  영상    → {os.path.basename(video_path)}\n")