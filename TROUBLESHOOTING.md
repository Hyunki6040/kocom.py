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

## 🔦 일괄소등 (Batch Switch) 문제 해결

### 증상
조명을 켜면 자동으로 일괄소등이 활성화되어 모든 조명이 꺼지는 현상

### 원인 분석
- 조명 제어 패킷(30bc 타입) 전송 시 월패드가 자동으로 일괄소등 모드를 활성화
- 일괄소등은 특수 패킷 타입(309c)을 사용하며 일반 조명 패킷과 다름

### 해결책: 연속 일괄소등 해제
조명 명령 후 5초간 일괄소등 OFF 패킷을 연속 전송하여 해제 상태 유지

**패킷 구조:**
```
일괄소등 ON:  aa55309c000eff01006500000000000000003f0d0d
일괄소등 OFF: aa55309c000eff010066ffffffffffffffff380d0d
```

**kocom.py 적용 방식:**
```python
BATCH_OFF_PACKET = 'aa55309c000eff010066ffffffffffffffff380d0d'

def send_batch_off_continuous(duration=5):
    """일괄소등 OFF 패킷을 연속으로 전송"""
    end_time = time.time() + duration
    count = 0
    while time.time() < end_time:
        rs485.write(bytearray.fromhex(BATCH_OFF_PACKET))
        count += 1
        time.sleep(0.3)
    logging.info('[BATCH_OFF] Sent {} times'.format(count))
```

### 디버깅 과정에서 배운 것

1. **단일 전송은 효과 없음**: 일괄소등 OFF를 한 번만 보내면 월패드가 다시 ON으로 전환
2. **타이밍 중요**: 0.3초 간격으로 5초간 연속 전송 (약 17회)이 안정적
3. **패킷 타입 구분**:
   - `30bc/30bd/30be`: 일반 조명 send/ack 패킷
   - `309c`: 일괄소등 전용 패킷 (특수 타입)
4. **src 주소**: 일괄소등 패킷은 `0100` (wallpad) 또는 `5400` 사용

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