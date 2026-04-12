import subprocess

# Appium 서버 포트 (기기별 독립 포트) 
APPIUM_PORTS = {
    "aos_emulator":  4723,
    "aos_real":      4725,
    "ios_simulator": 4727,
    "ios_real":      4729,
}


def get_appium_url(key: str) -> str:
    """key에 해당하는 Appium 서버 URL 반환 (항상 localhost 사용)"""
    port = APPIUM_PORTS[key]
    return f"http://127.0.0.1:{port}"


# Charles Proxy 설정 
CHARLES_PROXY = {
    "port": 8888,  # Charles Proxy 포트 (변경 시 여기만 수정)
}


def get_mac_ip() -> str:
    """
    현재 Mac의 로컬 IP 자동 감지
    - Wi-Fi(en0) 우선, 없으면 유선(en1) 시도
    - IP 변동되어도 자동으로 최신 IP 반환
    """
    try:
        for interface in ("en0", "en1"):
            result = subprocess.run(
                ["ipconfig", "getifaddr", interface],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
    except Exception:
        pass
    return "127.0.0.1"


def get_charles_proxy_host() -> str:
    """Charles Proxy 주소 반환 (Mac IP 자동 감지)"""
    return f"{get_mac_ip()}:{CHARLES_PROXY['port']}"


# 테스트 대상 URL
BASE_URL = "https://ridibooks.com"

# 타임아웃 (초)
TIMEOUT = {
    "implicit":    10,
    "explicit":    20,
    "page_load":   30,
    "new_command": 120,
    "adb_exec":    60000,
}

# Android 디바이스 정보 
AOS_DEVICE = {
    # "real": {
    #     "device_name": "YOUR_AOS_DEVICE_NAME",
    #     "udid":        "YOUR_AOS_DEVICE_UDID",  # 실기기 필수 (adb devices 로 확인)
    # },
    "emulator": {
        "device_name": "emulator-5554",
        "udid":        "",  # 1개 실행 시 생략, 여러 대 실행 시 adb devices 로 확인 후 기재
    },
}

# iOS 디바이스 정보
IOS_DEVICE = {
#     "real": {
#         "device_name":      "YOUR_IOS_DEVICE_NAME",
#         "udid":             "YOUR_IOS_DEVICE_UDID",  # 실기기 필수 (Xcode > Devices 에서 확인)
#         "platform_version": "17.0",
#     },
    "simulator": {
        "device_name":      "iPhone 16 Pro",
        "udid":             "",  # 1개 실행 시 생략, 여러 대 실행 시 xcrun simctl list 로 확인 후 기재
        "platform_version": "18.6",
    },
}

# 기타 경로
CHROMEDRIVER_PATH = "/path/to/chromedriver"

# 리포트 경로 (기기별 분리 + 타임스탬프)
REPORT_DIR = "reports"

REPORT_NAMES = {
    "aos_emulator":  "report_aos_emulator",
    "aos_real":      "report_aos_real",
    "ios_simulator": "report_ios_simulator",
    "ios_real":      "report_ios_real",
}


def get_report_path(key: str, timestamp: str = "") -> str:
    suffix = f"_{timestamp}" if timestamp else ""
    return f"{REPORT_DIR}/{REPORT_NAMES[key]}{suffix}.html"


# 스크린샷 경로 
SCREENSHOT_DIR = "screenshots"

# 로그 경로 
LOG_DIR = "logs"


# Tailscale 상태 

def _parse_exit_node_env(host_name: str) -> str:
    """
    Exit Node 호스트명에서 환경명 파싱
    - ridi-urbanbench-stage-exit-node  → stage
    - ridi-urbanbench-canary-exit-node → canary
    - ridi-urbanbench-exit-node        → prod
    """
    if "stage" in host_name:
        return "stage"
    elif "canary" in host_name:
        return "canary"
    return "prod"


def get_tailscale_status() -> dict:
    """
    Tailscale 연결 상태 및 Exit Node 환경 정보 반환
    - 활성화 시: {"active": True, "ip": "100.x.x.x", "env": "stage" | "canary" | "prod"}
    - 비활성화 시: {"active": False, "ip": None, "env": "prod"}
    """
    try:
        ip_result = subprocess.run(
            ["tailscale", "ip"],
            capture_output=True, text=True, timeout=3
        )
        status_result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True, text=True, timeout=3
        )

        if ip_result.returncode == 0 and ip_result.stdout.strip():
            import json
            ip    = ip_result.stdout.strip().split("\n")[0]
            data  = json.loads(status_result.stdout)
            peers = data.get("Peer", {}).values()
            env   = "prod"

            for peer in peers:
                if peer.get("ExitNode"):
                    env = _parse_exit_node_env(peer.get("HostName", ""))
                    break

            return {"active": True, "ip": ip, "env": env}

    except Exception:
        pass

    return {"active": False, "ip": None, "env": "prod"}