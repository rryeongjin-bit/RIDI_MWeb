import subprocess
import concurrent.futures
import argparse
import os
import re
import requests
from datetime import datetime
from config.settings import get_report_path, get_appium_url, get_tailscale_status, AOS_DEVICE, IOS_DEVICE

# 기기별 실행 마커 정의 
DEVICE_MARKERS = {
    "aos_emulator":  "aos and emulator and chrome",
    "aos_real":      "aos and real and samsung",
    "ios_simulator": "ios and simulator and safari",
    "ios_real":      "ios and real and safari",
}


# 기기 연결 상태 확인 
def check_aos_device(device_name: str) -> bool:
    """ADB로 AOS 기기 연결 상태 확인"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True, text=True
        )
        return device_name in result.stdout
    except Exception:
        return False


def check_ios_device(device_name: str) -> bool:
    """xcrun으로 iOS 시뮬레이터/실기기 연결 상태 확인"""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted"],
            capture_output=True, text=True
        )
        return device_name in result.stdout
    except Exception:
        return False


def check_device(target: str) -> bool:
    """기기 연결 상태 확인 (AOS/iOS 자동 분기)"""
    if "aos" in target:
        env = "emulator" if "emulator" in target else "real"
        device_name = AOS_DEVICE[env]["device_name"]
        return check_aos_device(device_name)
    else:
        env = "simulator" if "simulator" in target else "real"
        device_name = IOS_DEVICE[env]["device_name"]
        return check_ios_device(device_name)


# ── Appium 서버 health check ───────────────────────────────────────────

def check_appium_server(target: str) -> bool:
    """Appium 서버 실행 여부 확인"""
    url = get_appium_url(target)
    try:
        response = requests.get(f"{url}/status", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def validate_appium_servers(targets: list) -> list:
    """Appium 서버 + 기기 연결 상태 전체 확인"""
    valid_targets = []
    print(f"\n{'=' * 60}")
    print("  🔍 Appium 서버 + 기기 연결 상태 확인")
    print(f"{'=' * 60}")

    for target in targets:
        url        = get_appium_url(target)
        server_ok  = check_appium_server(target)
        device_ok  = check_device(target)

        if server_ok and device_ok:
            print(f"  ✅ {target:<20} | 서버 ✅ | 기기 ✅ → 실행 포함")
            valid_targets.append(target)
        elif not server_ok:
            print(f"  ❌ {target:<20} | 서버 ❌ | 기기 미확인 → 실행 제외")
        elif not device_ok:
            print(f"  ❌ {target:<20} | 서버 ✅ | 기기 ❌ → 실행 제외")

    if not valid_targets:
        print("\n  ⚠️  실행 가능한 기기가 없습니다. 종료합니다.")
        exit(1)

    print(f"{'=' * 60}")

    # Tailscale 연결 상태 출력 
    ts = get_tailscale_status()
    print(f"\n{'=' * 60}")
    print("  🔗 Tailscale 연결 상태")
    print(f"{'=' * 60}")
    if ts["active"]:
        print(f"  ✅ 활성화 | {ts['env']} 환경 연결 상태")
    else:
        print(f"  ⚪ 비활성화 | prod 환경 연결 상태")
    print(f"{'=' * 60}")

    return valid_targets


# pytest 실행 
def parse_test_counts(stdout: str) -> dict:
    """pytest 출력에서 실행된 함수 수, 성공/실패 수 파싱"""
    passed = len(re.findall(r" PASSED", stdout))
    failed = len(re.findall(r" FAILED", stdout))
    error  = len(re.findall(r" ERROR", stdout))
    total  = passed + failed + error
    return {"total": total, "passed": passed, "failed": failed, "error": error}


def run_pytest(target: str, marker_expr: str, report_path: str, keyword: str = "") -> dict:
    """기기 하나에 대한 pytest 실행 후 결과 반환"""
    os.makedirs("reports", exist_ok=True)

    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        f"-m={marker_expr}",
        f"--html={report_path}",
        "--self-contained-html",
        f"--device-key={target}",
    ]

    if keyword:
        cmd.append(f"-k={keyword}")

    result = subprocess.run(cmd, text=True, capture_output=True)
    counts = parse_test_counts(result.stdout)

    return {
        "target":     target,
        "marker":     marker_expr,
        "keyword":    keyword,
        "report":     report_path,
        "returncode": result.returncode,
        "stdout":     result.stdout,
        "stderr":     result.stderr,
        "counts":     counts,
    }


# 터미널 출력 
def print_result(result: dict):
    """기기별 실행 결과를 터미널에 구분하여 출력"""
    status = "✅ PASSED" if result["returncode"] == 0 else "❌ FAILED"
    sep    = "=" * 60
    c      = result["counts"]

    print(f"\n{sep}")
    print(f"  {status}  |  {result['target']}")
    print(f"  마커      : {result['marker']}")
    if result["keyword"]:
        print(f"  함수 필터 : {result['keyword']}")
    print(f"  실행 함수 : 총 {c['total']}개 | 성공 {c['passed']}개 | 실패 {c['failed']}개 | 에러 {c['error']}개")
    print(f"  리포트    : {result['report']}")
    print(sep)
    print(result["stdout"])
    if result["stderr"]:
        print("[STDERR]")
        print(result["stderr"])


# 메인 
def main():
    parser = argparse.ArgumentParser(description="모바일 웹 자동화 병렬 실행")
    parser.add_argument(
        "--targets", nargs="+",
        choices=list(DEVICE_MARKERS.keys()),
        default=list(DEVICE_MARKERS.keys()),
        help="실행할 기기 선택 (기본값: 전체)"
    )
    parser.add_argument(
        "--marker", type=str, default="",
        help="추가 마커 필터 (예: smoke, regression)"
    )
    parser.add_argument(
        "--keyword", type=str, default="",
        help="특정 함수명 필터링 (예: test_login, test_cart)"
    )
    args = parser.parse_args()

    # Appium 서버 + 기기 상태 확인
    valid_targets = validate_appium_servers(args.targets)

    # 타임스탬프
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 실행 목록 구성
    tasks = [
        (
            target,
            f"({DEVICE_MARKERS[target]}) and {args.marker}" if args.marker else DEVICE_MARKERS[target],
            get_report_path(target, timestamp),
        )
        for target in valid_targets
    ]

    print(f"\n{'=' * 60}")
    print(f"  🚀 자동화 테스트 시작 | {timestamp}")
    print(f"  실행 기기 수: {len(tasks)}개")
    if args.keyword:
        print(f"  함수 필터   : {args.keyword}")
    print(f"{'=' * 60}")
    for target, marker, report in tasks:
        print(f"  ▶ {target:<20} | 마커: {marker}")

    # 병렬 실행
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = [
            executor.submit(run_pytest, target, marker, report, args.keyword)
            for target, marker, report in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print_result(result)
            results.append(result)

    # 최종 요약 
    total_passed = sum(r["counts"]["passed"] for r in results)
    total_failed = sum(r["counts"]["failed"] for r in results)
    total_error  = sum(r["counts"]["error"]  for r in results)
    total_funcs  = sum(r["counts"]["total"]  for r in results)

    print(f"\n{'=' * 60}")
    print(f"  📊 최종 실행 요약 | {timestamp}")
    print(f"{'=' * 60}")

    # 기기별 상세 결과
    for r in sorted(results, key=lambda x: x["target"]):
        status = "✅" if r["returncode"] == 0 else "❌"
        c      = r["counts"]
        print(f"  {status} {r['target']:<20} | 총 {c['total']}개 | 성공 {c['passed']}개 | 실패 {c['failed']}개 | 에러 {c['error']}개")
        print(f"     리포트 → {r['report']}")

    print(f"\n  총 실행 기기  : {len(results)}개")
    print(f"  총 실행 함수  : {total_funcs}개")
    print(f"{'-' * 60}")

    # AOS/iOS 분류 결과
    aos_results = [r for r in results if "aos" in r["target"]]
    ios_results = [r for r in results if "ios" in r["target"]]

    if aos_results:
        aos_passed = sum(r["counts"]["passed"] for r in aos_results)
        aos_failed = sum(r["counts"]["failed"] for r in aos_results)
        aos_error  = sum(r["counts"]["error"]  for r in aos_results)
        print(f"  aos | 성공 {aos_passed}개 | 실패 {aos_failed}개 | 에러 {aos_error}개")

    if ios_results:
        ios_passed = sum(r["counts"]["passed"] for r in ios_results)
        ios_failed = sum(r["counts"]["failed"] for r in ios_results)
        ios_error  = sum(r["counts"]["error"]  for r in ios_results)
        print(f"  ios | 성공 {ios_passed}개 | 실패 {ios_failed}개 | 에러 {ios_error}개")

    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()