# 🔧 Kocom Wallpad RS485 - 문제 해결 가이드

## 📋 일반적인 문제 및 해결 방법

### 1. Socket Connection Timeout 오류

**증상:**
```
ERROR[2025-09-02 13:02:00,154]:[RS485] Socket connection failure : timed out | server 192.168.219.118, port 8899
```

**해결 방법:**

1. **kocom.conf 파일 확인** (`/share/kocom/kocom.conf`)
   - RS485 어댑터 타입 확인 (serial 또는 socket)
   - IP 주소와 포트가 정확한지 확인
   
2. **Serial 연결 사용 시:**
   ```ini
   [RS485]
   type = serial
   serial_port = /dev/ttyUSB0
   ```
   
3. **Socket 연결 사용 시:**
   ```ini
   [RS485]
   type = socket
   socket_server = 192.168.1.100  # 실제 RS485 어댑터 IP
   socket_port = 8899              # 실제 포트 번호
   ```

4. **네트워크 연결 확인:**
   - RS485 어댑터 전원 확인
   - 네트워크 케이블 연결 확인
   - ping 테스트: `ping 192.168.219.118`

### 2. MQTT Connection Failed

**증상:**
```
ERROR[MQTT] connection failure
```

**해결 방법:**

1. **Mosquitto broker 애드온 설치 확인**
   - 설정 → 애드온 → Mosquitto broker 설치 및 실행

2. **kocom.conf MQTT 설정:**
   ```ini
   [MQTT]
   mqtt_server = core-mosquitto  # 또는 HA IP 주소
   mqtt_port = 1883
   mqtt_allow_anonymous = False
   mqtt_username = homeassistant
   mqtt_password = your_password
   ```

3. **Mosquitto 사용자 생성:**
   - Mosquitto 애드온 설정에서 사용자 추가
   - kocom.conf에 동일한 사용자 정보 입력

### 3. Serial Port Not Found

**증상:**
```
ERROR[RS485] Serial open failure : [Errno 2] could not open port /dev/ttyUSB0
```

**해결 방법:**

1. **USB 장치 연결 확인:**
   ```bash
   ls /dev/tty*
   ```

2. **config.yaml에서 uart 활성화 확인:**
   ```yaml
   uart: true
   ```

3. **권한 문제 해결:**
   - Home Assistant 재시작
   - USB 장치 재연결

### 4. 403 Forbidden 설치 오류

**증상:**
```
Can't install ghcr.io/home-assistant/aarch64-addon-kocom:2025.01.001: 403 Client Error
```

**해결 방법:**
- 최신 버전 (2025.01.002+) 사용
- config.yaml에서 `image` 필드 제거됨 확인

## 🔍 디버깅 방법

### 로그 확인
1. Home Assistant → 설정 → 애드온 → Kocom Wallpad
2. 로그 탭에서 실시간 로그 확인

### 디버그 모드 활성화
kocom.conf 파일에서:
```ini
[Log]
show_query_hex = True
show_recv_hex = True
show_mqtt_publish = True
```

### 수동 테스트
```bash
# MQTT 메시지 모니터링
mosquitto_sub -h localhost -p 1883 -t 'kocom/#' -v

# RS485 연결 테스트 (Socket)
telnet 192.168.219.118 8899

# RS485 연결 테스트 (Serial)
screen /dev/ttyUSB0 9600
```

## 🔄 자동 복구 기능

v2025.01.002부터 자동 재시도 기능이 추가되었습니다:

1. **연결 재시도**: 최대 10회, 점진적 대기 시간
2. **자동 재시작**: 연결 실패 시 60초 후 재시작
3. **상세한 오류 메시지**: 문제 진단을 위한 구체적인 안내

## 💡 추가 팁

1. **RS485 어댑터 설정**
   - Baud rate: 9600
   - Data bits: 8
   - Stop bits: 1
   - Parity: None

2. **네트워크 RS485 어댑터 (Elfin EW11 등)**
   - TCP Server 모드 설정
   - 포트: 8899 (기본값)
   - Keep Alive 활성화

3. **Home Assistant 통합**
   - MQTT Discovery 자동 감지
   - Entity 자동 생성

## 📞 지원

추가 도움이 필요하시면:
- GitHub Issues: https://github.com/Hyunki6040/kocom.py/issues
- 네이버 카페: https://cafe.naver.com/koreassistant