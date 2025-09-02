# 🏠 Kocom Wallpad RS485 for Home Assistant

[![Version](https://img.shields.io/badge/version-2025.01.009-blue.svg)](https://github.com/Hyunki6040/kocom.py)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.x-brightgreen.svg)](https://www.home-assistant.io/)
[![Python](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Auto-update](https://img.shields.io/badge/auto--update-enabled-success.svg)](AUTO_UPDATE.md)

**덕계역금강펜트리움** 전용 Kocom 월패드 Home Assistant 통합 애드온

> 🚀 **v2025 완전 리뉴얼!** Python 3.12, HA 2025.x 완벽 호환, UI 설정 지원, Auto-update 기능

---

## ✨ 주요 기능

### 🎯 핵심 기능
- ✅ **완전한 UI 설정** - 파일 편집 불필요!
- ✅ **Auto-update** - 자동 업데이트 지원
- ✅ **MQTT Discovery** - 자동 엔티티 생성
- ✅ **실시간 상태 동기화** - 양방향 통신
- ✅ **자동 재연결** - 연결 끊김 시 자동 복구

### 📱 지원 장치
| 장치 | 엔티티 타입 | 기능 |
|------|------------|------|
| 🌀 **환기(Fan)** | `fan.*` | 속도 조절 (Low/Medium/High) |
| 🛗 **엘리베이터** | `switch.*` | 호출 |
| 💡 **조명** | `light.*` | 각 방 3개씩 개별 제어 |
| 🌡️ **온도조절기** | `climate.*` | 온도 설정, 켜기/끄기 |
| ❄️ **에어컨** | `climate.*` | 온도, 모드, 풍량 조절 |

### 🔧 연결 방식
- **Serial (USB RS485)** - USB to RS485 어댑터
- **Socket (Network)** - Elfin EW11 등 네트워크 RS485 어댑터

---

## 🚀 빠른 시작 (3분 설치!)

### 1️⃣ 저장소 추가
**설정** → **애드온** → **애드온 스토어** → **⋮** → **저장소**

```
https://github.com/Hyunki6040/kocom.py
```

### 2️⃣ 애드온 설치
1. 스토어에서 **"Kocom Wallpad with RS485 for 덕계역금강펜트리움"** 찾기
2. **INSTALL** 클릭 (5-10분 소요)

### 3️⃣ 설정 (UI에서!)
**Configuration** 탭에서:

#### Socket 연결 (Elfin EW11)
```yaml
RS485 Type: socket
Socket Server: 192.168.0.222  # 당신의 EW11 IP
Socket Port: 8899
MQTT Allow Anonymous: true
```

#### Serial 연결 (USB)
```yaml
RS485 Type: serial
Serial Port: /dev/ttyUSB0
MQTT Allow Anonymous: true
```

### 4️⃣ 시작
**START** 버튼 클릭 → 완료! 🎉

---

## 🔄 Auto-update 설정

**Info** 탭 → **Auto update** 토글 ON → 끝!

이제 자동으로 업데이트됩니다. [자세히 보기](AUTO_UPDATE.md)

---

## 📊 상태 확인

### Home Assistant 대시보드
```yaml
type: vertical-stack
cards:
  - type: entities
    title: 코콤 월패드
    entities:
      - fan.kocom_wallpad_fan
      - switch.kocom_wallpad_elevator
      
  - type: horizontal-stack
    cards:
      - type: light
        entity: light.kocom_livingroom_light1
        name: 거실
      - type: light
        entity: light.kocom_room1_light1
        name: 방1
        
  - type: thermostat
    entity: climate.kocom_livingroom_thermostat
    name: 거실 온도
```

### MQTT Explorer
- Topic: `kocom/#`
- 실시간 데이터 모니터링

---

## 🔧 문제 해결

### ❌ Socket 연결 실패
```
ERROR: Socket connection failure: timed out
```
**해결**: 
- EW11 IP 주소 확인
- 포트 8899 확인
- 전원 및 네트워크 케이블 확인

### ❌ MQTT 연결 실패
```
Client <unknown> closed its connection
```
**해결**: 
- Configuration에서 `MQTT Allow Anonymous: true` 설정
- Mosquitto broker 애드온 설치 확인

### ❌ Serial 포트 없음
```
ERROR: Serial open failure
```
**해결**:
- USB 케이블 연결 확인
- `ls /dev/tty*` 명령으로 포트 확인
- config.yaml에 `uart: true` 확인

> 더 자세한 문제 해결: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 문서

| 문서 | 설명 |
|-----|------|
| 📋 [QUICK_INSTALL.md](QUICK_INSTALL.md) | 빠른 설치 가이드 |
| 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 상세한 문제 해결 |
| 🔄 [AUTO_UPDATE.md](AUTO_UPDATE.md) | 자동 업데이트 설정 |
| 📡 [MQTT_SETUP.md](MQTT_SETUP.md) | MQTT 설정 가이드 |
| 📝 [CHANGELOG.md](CHANGELOG.md) | 변경 내역 |

---

## 🛠️ 기술 사양

### 시스템 요구사항
- Home Assistant 2025.x 이상
- Python 3.12 (Alpine Linux)
- Mosquitto broker 애드온

### RS485 설정
- Baud rate: 9600
- Data bits: 8
- Stop bits: 1
- Parity: None

### 지원 아키텍처
- `aarch64` (Raspberry Pi 4/5)
- `amd64` (Intel/AMD)
- `armhf` (Raspberry Pi 3)
- `armv7` (기타 ARM)
- `i386` (32bit)

---

## 👨‍💻 개발

### 로컬 빌드
```bash
# Clone
git clone https://github.com/Hyunki6040/kocom.py.git
cd kocom.py

# Build
docker build -t kocom-wallpad .

# Run
docker run -v /share:/share kocom-wallpad
```

### 디버그 모드
Configuration에서 `Debug Mode: true` 활성화

로그 확인:
```bash
docker logs addon_kocom_py
```

---

## 🤝 기여

버그 리포트 및 기능 제안 환영합니다!

1. Issue 생성: [GitHub Issues](https://github.com/Hyunki6040/kocom.py/issues)
2. Pull Request 환영
3. 네이버 카페: [Korea Assistant](https://cafe.naver.com/koreassistant)

---

## 📜 라이선스

MIT License - 자유롭게 사용 및 수정 가능

---

## 🙏 감사의 말

원작자 및 기여자:
- vifrost (원작자)
- kyet, 룰루해피, 따분, Susu Daddy, harwin1
- 그리고 모든 테스터 분들

---

## 📞 연락처

- **관리자**: robert
- **아파트**: 덕계역금강펜트리움
- **GitHub**: [Hyunki6040/kocom.py](https://github.com/Hyunki6040/kocom.py)
- **버전**: 2025.01.009

---

<div align="center">
  
**⭐ 도움이 되셨다면 Star를 눌러주세요!**

[![GitHub stars](https://img.shields.io/github/stars/Hyunki6040/kocom.py?style=social)](https://github.com/Hyunki6040/kocom.py)

</div>