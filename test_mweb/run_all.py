
# 사용법:
#   전체 기기 병렬 실행        : python run_all.py
#   특정 기기만 선택 실행      : python run_all.py --targets aos_emulator ios_simulator
#   특정 마커 케이스만 실행    : python run_all.py --marker smoke
#   기기 + 마커 조합 실행      : python run_all.py --targets aos_emulator --marker smoke

import subprocess
import concurrent.futures
import argparse
import os
import requests
from datetime import datetime
from config.settings import *

# 기기별 실행 마커 정의
DEVICE_MARKERS = {
    "aos_emulator":  "aos and emulator",
    "aos_real":      "aos and real",
    "ios_simulator": "ios and simulator",
    "ios_real":      "ios and real",
}

# Appium 서버 health check
def check_appium_server(target: str) -> bool:
    """Appium 서버 실행 여부 확인"""
    url = get_appium_url(target)
    try:
        response = requests.get(f"{url}/status", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def validate_appium_servers(targets: list) -> list:
    """
    실행 대상 기기의 Appium 서버 상태 전체 확인
    - 서버 미실행 기기는 실행 목록에서 제외 후 경고 출력
    - 전체 미실행 시 종료
    """
    valid_targets = []
    print(f"\n{'=' * 60}")
    print("  🔍 Appium 서버 상태 확인")
    print(f"{'=' * 60}")

    for target in targets:
        url = get_appium_url(target)
        if check_appium_server(target):
            print(f"  ✅ {target:<20} | {url} 연결 확인")
            valid_targets.append(target)
        else:
            print(f"  ❌ {target:<20} | {url} 연결 실패 → 실행 제외")

    if not valid_targets:
        print("\n  ⚠️  실행 가능한 Appium 서버가 없습니다. 종료합니다.")
        exit(1)

    print(f"{'=' * 60}")
    return valid_targets


# pytest 실행
def run_pytest(target: str, marker_expr: str, report_path: str) -> dict:
    """기기 하나에 대한 pytest 실행 후 결과 반환"""
    os.makedirs("reports", exist_ok=True)

    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        f"-m={marker_expr}",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    result = subprocess.run(cmd, text=True, capture_output=True)

    return {
        "target":     target,
        "marker":     marker_expr,
        "report":     report_path,
        "returncode": result.returncode,
        "stdout":     result.stdout,
        "stderr":     result.stderr,
    }


# 터미널 출력
def print_result(result: dict):
    """기기별 실행 결과를 터미널에 구분하여 출력"""
    status = "✅ PASSED" if result["returncode"] == 0 else "❌ FAILED"
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  {status}  |  {result['target']}")
    print(f"  마커    : {result['marker']}")
    print(f"  리포트  : {result['report']}")
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
    args = parser.parse_args()

    # Appium 서버 상태 확인 → 미실행 기기 제외
    valid_targets = validate_appium_servers(args.targets)

    # 실행 시점 타임스탬프 (같은 세션은 동일한 타임스탬프 공유)
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
    print(f"{'=' * 60}")
    for target, marker, report in tasks:
        print(f"  ▶ {target:<20} | 마커: {marker}")

    # 병렬 실행
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = [
            executor.submit(run_pytest, target, marker, report)
            for target, marker, report in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print_result(result)
            results.append(result)

    # 최종 요약
    passed = [r for r in results if r["returncode"] == 0]
    failed = [r for r in results if r["returncode"] != 0]

    print(f"\n{'=' * 60}")
    print(f"  📊 최종 실행 요약 | {timestamp}")
    print(f"{'=' * 60}")
    for r in sorted(results, key=lambda x: x["target"]):
        status = "✅" if r["returncode"] == 0 else "❌"
        print(f"  {status}  {r['target']:<20} → {r['report']}")
    print(f"{'-' * 60}")
    print(f"  총 {len(results)}개 기기 | 성공: {len(passed)}개 | 실패: {len(failed)}개")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()