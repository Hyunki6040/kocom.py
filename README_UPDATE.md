# 🚀 Kocom Wallpad RS485 for 덕계역금강펜트리움 - Home Assistant 2025.x 업데이트 완료

**Maintained by robert**

## 📋 주요 변경사항

### 1. **Python 버전 업그레이드** ✅
- Python 3.7.3 → **Python 3.12 Alpine** (최신 버전)
- 더 작은 이미지 크기와 향상된 보안

### 2. **종속성 문제 해결** ✅
- `typing.Literal` 오류 완전 해결
- `paho-mqtt` 2.1.0 (최신 버전) 지원
- `requirements.txt` 파일 추가로 명확한 종속성 관리

### 3. **Home Assistant 2025.x 호환성** ✅
- 최신 HA 애드온 구조 적용
- MQTT Discovery 자동 설정
- 향상된 서비스 통합

### 4. **코드 현대화** ✅
- Type hints 추가 (Python 3.12 기능 활용)
- paho-mqtt 2.x API 호환성 적용
- 에러 처리 개선

## 🛠️ 설치 방법

### 방법 1: Fork 후 개인 저장소 사용 (권장)

1. **Home Assistant에 저장소 추가**
   - 설정 → 애드온 → 애드온 스토어 → ⋮ → 저장소
   - 추가: `https://github.com/Hyunki6040/kocom.py`

3. **애드온 설치**
   - 스토어에서 "Kocom Wallpad with RS485" 찾기
   - 설치 → 시작

### 방법 2: 로컬 빌드 (개발자용)

```bash
# 빌드 스크립트 실행
./build.sh

# 또는 수동 빌드
docker build -t kocom-wallpad:latest .
```

## 📝 설정 예시

### kocom.conf (자동 생성됨)
```ini
[RS485]
type = serial
serial_port = /dev/ttyUSB0

[MQTT]
mqtt_server = 192.168.1.100  # HA IP 주소
mqtt_port = 1883
mqtt_allow_anonymous = False
mqtt_username = homeassistant
mqtt_password = your_password

[Device]
enabled = light_livingroom, light_room1, thermo_livingroom, fan
```

## 🔧 문제 해결

### 오류: "Module not found"
→ 애드온 재설치 필요 (새 이미지 빌드됨)

### 오류: "MQTT connection failed"
→ Mosquitto broker 애드온 설치 확인
→ 사용자명/비밀번호 확인

### 오류: "Serial port not found"
→ config.yaml에서 `uart: true` 확인
→ USB 장치 연결 확인: `ls /dev/tty*`

## 📚 변경된 파일 목록

- ✅ `Dockerfile` - Python 3.12 Alpine 사용
- ✅ `requirements.txt` - 명확한 종속성 관리 (신규)
- ✅ `config.yaml` - HA 2025.x 호환성
- ✅ `kocom.py` - paho-mqtt 2.x API 지원
- ✅ `run.sh` - 개선된 시작 스크립트
- ✅ `build.sh` - 쉬운 빌드 스크립트 (신규)

## 🎯 테스트 완료 항목

- [x] Python 3.12 호환성
- [x] paho-mqtt 2.1.0 연결
- [x] Home Assistant 2025.8.3 통합
- [x] MQTT Discovery
- [x] RS485 시리얼 통신
- [x] 소켓 통신 모드

## 💡 추가 개선 제안

1. **환경 변수 지원**: 설정을 환경 변수로도 관리 가능
2. **Health Check**: 컨테이너 상태 모니터링
3. **자동 재시작**: 연결 실패 시 자동 복구
4. **웹 UI 설정**: HA 인터페이스에서 직접 설정

---

**버전**: 2025.01.004  
**호환성**: Home Assistant 2025.8.x 이상  
**Python**: 3.12 (Alpine Linux)  
**작성자**: robert  
**아파트**: 덕계역금강펜트리움  
**업데이트 날짜**: 2025-01-02