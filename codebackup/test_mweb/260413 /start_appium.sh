

HOST="127.0.0.1"
PROXY_PORT=8888

# 포트 정의 
AOS_EMULATOR_PORT=4723
AOS_REAL_PORT=4725
IOS_SIMULATOR_PORT=4727
IOS_REAL_PORT=4729

# Mac IP 자동 감지
get_mac_ip() {
    MAC_IP=$(ipconfig getifaddr en0 2>/dev/null)
    if [ -z "$MAC_IP" ]; then
        MAC_IP=$(ipconfig getifaddr en1 2>/dev/null)
    fi
    if [ -z "$MAC_IP" ]; then
        echo "⚠️  Mac IP를 감지할 수 없습니다."
        exit 1
    fi
    echo $MAC_IP
}

# 프록시 설정 
setup_proxy() {
    MAC_IP=$(get_mac_ip)
    PROXY="$MAC_IP:$PROXY_PORT"

    echo "\n📡 프록시 설정 중... ($PROXY)"

    # AOS 에뮬레이터 프록시 설정
    if adb devices 2>/dev/null | grep -q "emulator"; then
        adb -s emulator-5554 shell settings put global http_proxy $PROXY
        echo "  ✅ AOS 에뮬레이터 프록시 설정 완료 ($PROXY)"
    fi

    # AOS 실기기 프록시 설정
    if adb devices 2>/dev/null | grep -q "device$"; then
        for DEVICE in $(adb devices | grep "device$" | awk '{print $1}'); do
            adb -s $DEVICE shell settings put global http_proxy $PROXY
            echo "  ✅ AOS 실기기 프록시 설정 완료 ($DEVICE / $PROXY)"
        done
    fi

    # iOS 시뮬레이터 프록시 설정 (Mac 시스템 프록시)
    networksetup -setwebproxy Wi-Fi $MAC_IP $PROXY_PORT 2>/dev/null
    networksetup -setsecurewebproxy Wi-Fi $MAC_IP $PROXY_PORT 2>/dev/null
    echo "  ✅ iOS 시뮬레이터 프록시 설정 완료 (Mac 시스템 프록시)"
    echo "  ℹ️  iOS 실기기는 기기에서 Wi-Fi 프록시 수동 설정 필요"
    echo "      → 설정 → Wi-Fi → 연결된 네트워크 → 프록시 구성 → 수동"
    echo "      → 서버: $MAC_IP / 포트: $PROXY_PORT"
}

# 프록시 해제 
remove_proxy() {
    echo "\n📡 프록시 해제 중..."

    # AOS 프록시 해제
    adb shell settings put global http_proxy :0 2>/dev/null
    echo "  ✅ AOS 프록시 해제 완료"

    # iOS 시뮬레이터 프록시 해제 (Mac 시스템 프록시)
    networksetup -setwebproxystate Wi-Fi off 2>/dev/null
    networksetup -setsecurewebproxystate Wi-Fi off 2>/dev/null
    echo "  ✅ iOS 시뮬레이터 프록시 해제 완료"
    echo "  ℹ️  iOS 실기기는 기기에서 수동 해제 필요"
}

# 서버 종료 
stop_servers() {
    echo "\n🛑 Appium 서버 전체 종료 중..."
    for PORT in $AOS_EMULATOR_PORT $AOS_REAL_PORT $IOS_SIMULATOR_PORT $IOS_REAL_PORT; do
        PID=$(lsof -ti :$PORT)
        if [ -n "$PID" ]; then
            kill -9 $PID
            echo "  ✅ 포트 $PORT 종료 완료 (PID: $PID)"
        else
            echo "  ⚪ 포트 $PORT 실행 중이지 않음"
        fi
    done
    echo "🛑 Appium 서버 종료 완료"
}

# 단일 포트 서버 실행 
start_single() {
    PORT=$1
    LOG_FILE="logs/appium_${PORT}.log"
    mkdir -p logs

    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo "  ⚠️  포트 $PORT 이미 실행 중 → 재시작"
        kill -9 $PID
        sleep 1
    fi

    appium -p $PORT --address $HOST > $LOG_FILE 2>&1 &
    echo "  ✅ 포트 $PORT 시작 | 주소: $HOST:$PORT | 로그: $LOG_FILE"
}

# 메인 실행
if [ "$1" = "stop" ]; then
    remove_proxy
    stop_servers

elif [ "$1" = "proxy" ]; then
    setup_proxy

elif [ -n "$1" ]; then
    echo "\n🚀 Appium 서버 시작 (포트: $1)"
    start_single $1

else
    # 전체 실행: 프록시 설정 + 전체 포트 실행
    setup_proxy

    echo "\n🚀 Appium 서버 전체 시작 | HOST: $HOST"
    start_single $AOS_EMULATOR_PORT
    start_single $AOS_REAL_PORT
    start_single $IOS_SIMULATOR_PORT
    start_single $IOS_REAL_PORT
fi

echo "\n✅ 완료"