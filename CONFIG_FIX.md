# 🔧 설정 파일 수정 방법

## ⚠️ 현재 문제
- 설정 파일에 이전 IP 주소가 남아있음 (192.168.219.118)
- 당신이 입력한 IP (39.125.16.174)가 적용되지 않음

## ✅ 즉시 해결 방법

### 방법 1: Home Assistant File Editor 사용

1. **File Editor 애드온 설치** (없다면)
   - 설정 → 애드온 → File Editor 검색 → 설치

2. **설정 파일 열기**
   - File Editor에서 `/share/kocom/kocom.conf` 열기

3. **다음 내용으로 전체 교체**:
```ini
[RS485]
type = socket
socket_server = 39.125.16.174
socket_port = 8899

[MQTT]
mqtt_server = core-mosquitto
mqtt_port = 1883
mqtt_allow_anonymous = False
mqtt_username = homeassistant
mqtt_password = your_password_here

[Device]
enabled = fan, elevator, light_livingroom, light_room1, light_room2, light_room3, light_kitchen, thermo_livingroom, thermo_room1, thermo_room2, thermo_room3

[Elevator]
type = rs485
rs485_floor = 15

[Log]
show_query_hex = True
show_recv_hex = True
show_mqtt_publish = True
show_mqtt_discovery = False

[User]
init_temp = 23
init_fan_mode = Medium
light_count = 3
thermo_init_temp = 23
ac_init_temp = 21
ac_init_mode = cool
fan_init_fan_mode = low
ac_init_fan_mode = LOW
```

4. **저장 후 애드온 재시작**

### 방법 2: SSH & Terminal 사용

1. **Terminal 애드온에서**:
```bash
# 백업
cp /share/kocom/kocom.conf /share/kocom/kocom.conf.backup

# 파일 편집
nano /share/kocom/kocom.conf
```

2. **IP 주소 변경**:
   - `socket_server = 192.168.219.118` → `socket_server = 39.125.16.174`
   - 중복된 `type` 항목 제거

3. **저장**: Ctrl+X → Y → Enter

4. **애드온 재시작**

### 방법 3: 설정 파일 삭제 후 재생성

1. **Terminal에서**:
```bash
# 기존 파일 삭제
rm /share/kocom/kocom.conf

# 애드온 재시작 (새 파일 자동 생성)
```

2. **새로 생성된 파일 편집**
   - IP 주소를 39.125.16.174로 변경

## 🔍 설정 확인

애드온 재시작 후 로그에서 확인:
```
[Info] Current RS485 configuration:
[Info]   type = socket
[Info]   socket_server = 39.125.16.174  ← 이렇게 나와야 정상!
[Info]   socket_port = 8899
```

## 💡 참고사항

- **MQTT 비밀번호**: `your_password_here`를 실제 비밀번호로 변경
- **Mosquitto 설정**: Home Assistant 사용자명과 비밀번호 확인
- **포트 번호**: Elfin EW11의 기본값은 8899

## 🆘 여전히 문제가 있다면

1. 애드온 완전 재설치
2. `/share/kocom` 폴더 전체 삭제 후 재시작
3. GitHub Issues에 문제 제보