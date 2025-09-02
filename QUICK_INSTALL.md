# 🚀 빠른 설치 가이드 - 덕계역금강펜트리움 Kocom 애드온

## 📌 설치 URL
```
https://github.com/Hyunki6040/kocom.py
```

## 🔧 설치 단계

### 1️⃣ Home Assistant 저장소 추가
1. **설정** → **애드온** → **애드온 스토어**
2. 우측 상단 **⋮** (점 3개) 클릭
3. **저장소** 클릭
4. 위 URL 복사 & 붙여넣기
5. **추가** 버튼 클릭

### 2️⃣ 애드온 설치
1. 스토어 하단에서 **"Kocom Wallpad with RS485 for 덕계역금강펜트리움"** 찾기
2. **INSTALL** 클릭 (약 5-10분 소요)
3. 설치 완료 후 **START** 클릭

### 3️⃣ 설정 수정
**위치**: `/share/kocom/kocom.conf`

**USB RS485 사용 시:**
```ini
[RS485]
type = serial
serial_port = /dev/ttyUSB0

[MQTT]
mqtt_server = core-mosquitto
mqtt_username = homeassistant
mqtt_password = 비밀번호
```

**네트워크 RS485 사용 시 (Elfin EW11 등):**
```ini
[RS485]
type = socket
socket_server = 192.168.1.100  # RS485 어댑터 IP
socket_port = 8899

[MQTT]
mqtt_server = core-mosquitto
mqtt_username = homeassistant
mqtt_password = 비밀번호
```

### 4️⃣ 애드온 재시작
설정 변경 후 반드시 애드온 재시작!

## ✅ 설치 확인
- 애드온 로그에서 연결 성공 메시지 확인
- MQTT Explorer에서 `kocom/#` 토픽 확인

## 🆘 문제 발생 시
- TROUBLESHOOTING.md 참조
- GitHub Issues: https://github.com/Hyunki6040/kocom.py/issues

---
**버전**: 2025.01.004  
**관리자**: robert  
**아파트**: 덕계역금강펜트리움