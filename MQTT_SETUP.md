# 🔧 MQTT 설정 가이드 - Mosquitto 연결 문제 해결

## ❌ 문제 증상

### 1. Anonymous 연결 거부
```
DEBUG: Received CONNACK (0, 5) 
ERROR: Connection error - Not authorized: Not authorized
```
- **Error Code 5**: 브로커가 익명 연결을 허용하지 않음

### 2. 연결 즉시 끊김  
```
New connection from 172.30.32.2:34498 on port 1883.
Client <unknown> closed its connection.
```
- `<unknown>`: CONNECT 패킷을 보내지 못하고 즉시 연결이 끊어짐

## ✅ 해결 방법

### 방법 1: Mosquitto 브로커 Anonymous 허용 (권장) 🎯

**먼저 Mosquitto Broker 애드온 설정:**

1. **설정 → 애드온 → Mosquitto broker → Configuration**
2. **다음과 같이 설정:**
   ```yaml
   logins: []  # 비워두기
   anonymous: true  # 반드시 true
   customize:
     active: false
     folder: mosquitto
   ```

**그 다음 Kocom 애드온 Configuration:**
```yaml
mqtt_allow_anonymous: true
mqtt_username: ""  # 비워두기
mqtt_password: ""  # 비워두기
```

**장점**: 
- 가장 간단하고 안정적
- Home Assistant 내부 네트워크에서만 작동하므로 안전
- 인증 충돌 없음

⚠️ **중요**: Mosquitto 브로커에서 `anonymous: true` 설정 필수!

### 방법 2: 전용 사용자 계정 생성 (권장) ✅

1. **Mosquitto 브로커 설정**:
   ```yaml
   logins:
     - username: YOUR_USERNAME
       password: YOUR_PASSWORD
   anonymous: false
   ```

2. **Kocom 애드온 Configuration 설정**:
   ```yaml
   mqtt_allow_anonymous: false
   mqtt_username: "YOUR_USERNAME"
   mqtt_password: "YOUR_PASSWORD"
   ```

3. **애드온 재시작**:
   - Mosquitto broker 재시작
   - Kocom 애드온 재시작

### 방법 3: Home Assistant 사용자 활용

**주의**: `hk_admin` 같은 관리자 계정 사용 비추천!

```yaml
mqtt_username: "일반사용자명"
mqtt_password: "비밀번호"
```

## 🔍 디버깅 체크리스트

### 1. Mosquitto 로그 확인
```bash
# 정상 연결
New client connected from 172.30.32.2:xxxxx as kocom_XXXXXXXX (p2, c1, k60)

# 실패 (인증 문제)
Client <unknown> disconnected due to malformed packet.

# 실패 (연결 즉시 끊김)
Client <unknown> closed its connection.
```

### 2. 네트워크 확인
- Kocom 애드온과 Mosquitto가 같은 Docker 네트워크에 있는지 확인
- `core-mosquitto` 호스트명이 올바른지 확인

### 3. 포트 확인
- **1883**: 평문 연결 (일반적)
- **8883**: TLS/SSL 연결
- Kocom은 1883 사용!

## 🚀 권장 설정 (v2025.01.008)

**애드온 Configuration 탭**:
```yaml
RS485 Type: socket
Socket Server: 192.168.0.222
Socket Port: 8899
MQTT Server: core-mosquitto
MQTT Port: 1883
MQTT Allow Anonymous: false
MQTT Username: YOUR_USERNAME
MQTT Password: YOUR_PASSWORD
```

## 📊 연결 확인

성공 시 로그:
```
INFO[MQTT] connecting (anonymous) to core-mosquitto:1883
INFO[MQTT] Connected - 0: OK
INFO[MQTT] Subscribed: 1 [ReasonCode(Suback, 'Granted QoS 0')]
```

## 🆘 여전히 안 되면?

1. **Mosquitto 브로커 재시작**
2. **모든 애드온 재시작** (순서: Mosquitto → Kocom)
3. **Home Assistant Core 재시작**

---

**참고**: Home Assistant 애드온 간 통신은 내부 Docker 네트워크에서 이루어지므로, Anonymous 연결도 안전합니다!