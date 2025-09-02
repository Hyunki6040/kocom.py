# 📝 CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2025.01.010] - 2025-01-02

### 🐛 Fixed
- MQTT authorization error (`Not authorized`) - fixed anonymous connection handling
- MQTT callback function signatures for paho-mqtt 2.x compatibility
- `mqtt_on_disconnect()` TypeError - added properties parameter

### 📝 Changed
- Removed unnecessary contact information from README
- Updated CHANGELOG format for better tracking

---

## [2025.01.009] - 2025-01-02

### ✨ Added
- **Auto-update support** - no more manual updates needed!
- GitHub Actions workflow for automatic releases
- `updater.json` for version tracking
- Comprehensive AUTO_UPDATE.md documentation

### 📝 Changed
- Added `stage: stable` and `auto_update: true` to config.yaml

---

## [2025.01.008] - 2025-01-02

### 🐛 Fixed
- MQTT `<unknown>` connection issue
- Generate unique client ID for each connection
- Set `clean_session=True` and `protocol=MQTTv311` explicitly
- Added exponential backoff for reconnection attempts

### 📝 Changed
- Default to anonymous MQTT connection (more stable for addon-to-addon)
- Improved MQTT error logging with detailed messages

### 📚 Added
- MQTT_SETUP.md troubleshooting guide

---

## [2025.01.007] - 2025-01-02

### 🐛 Fixed
- Missing `show_mqtt_discovery` option in Log configuration
- `mqtt_on_subscribe()` signature for paho-mqtt 2.x
- Added all missing User configuration options

### ✅ Status
- RS485 connection working (192.168.0.222:8899)
- MQTT connection successful
- Data receiving normally

---

## [2025.01.006] - 2025-01-02

### 📝 Changed
- Updated default socket server IP to 192.168.0.222
- Updated kocom.conf.example with new IP

---

## [2025.01.005] - 2025-01-02

### ✨ Added
- **Full UI configuration support** via Home Assistant addon options
- Read settings from `/data/options.json` instead of manual kocom.conf
- Automatic fallback to kocom.conf if UI options not available

### 📝 Changed
- All settings now configurable from addon Configuration tab
- No more manual file editing required!

---

## [2025.01.004] - 2025-01-02

### 📝 Changed
- Updated project name to "덕계역금강펜트리움"
- Updated maintainer to "robert"
- Updated all documentation and configuration files

---

## [2025.01.003] - 2025-01-02

### 🐛 Fixed
- Connection retry logic with exponential backoff (max 10 retries)
- Socket connection error messages with specific diagnostics
- Auto-restart capability in run.sh (60s delay on failure)

### 📝 Changed
- Default kocom.conf to use serial connection (more stable)
- Display current configuration on startup

### 📚 Added
- Comprehensive TROUBLESHOOTING.md guide

---

## [2025.01.002] - 2025-01-02

### 🐛 Fixed
- Removed external Docker image reference causing 403 error
- Updated repository URL to correct GitHub repo

---

## [2025.01.001] - 2025-01-02

### 🚀 Fork Started by robert
**Major rewrite for Home Assistant 2025.x compatibility**

### ✨ Added
- Python 3.12 support (upgraded from 3.7)
- paho-mqtt 2.x compatibility
- Type hints for Python 3.12
- requirements.txt for explicit dependency management
- Modern HA addon structure
- CLAUDE.md for AI assistance
- README_UPDATE.md with comprehensive guide
- build.sh for easy deployment

### 🐛 Fixed
- `typing.Literal` import error (Python 3.7 incompatibility)
- `typing_extensions` module not found error
- paho-mqtt version conflicts

### 📝 Changed
- Base Docker image from `python:3.7.3` to `python:3.12-alpine`
- Updated all dependencies to latest stable versions
- Modernized code with Python 3.12 features
- Improved error handling and logging

### 🔧 Technical
- Alpine Linux for smaller image size
- Better Docker layer caching
- Explicit version pinning in requirements.txt

---

## [Original Version] - Before 2025

### Original Development by vifrost

Based on work by:
- vifrost (original author)
- kyet
- 룰루해피
- 따분
- Susu Daddy
- harwin1

### Historical Changes (from original README)

- (2023-08-03) harwin1 에어컨 소스 반영
- (2022-11-07) bedroom 삭제, room1,2,3으로 변경, kitchen 추가
- (2022-07-24) config.json을 config.yaml로 변환
- (2022-04-10) MQTT Discovery 지원
- (2022-03-30) Home Assistant Supervisor Add-on에서 실행되도록 수정
- (2022-03-29) 전열교환기(Fan) 프리셋모드 추가
- (2020-09-25) 엘리베이터 도착정보 추가
- (2019-12-09) GitHub 개설, serial 강제 종료시 error handling
- (2019-11-19) 패킷발송 후 기기상태 수신시까지 다음패킷 발송 방지
- (2019-11-18) polling 도중 command 발생시 간헐적 충돌 해결
- (2019-11-17) RS485/MQTT 연결 끊김 예외처리/자동복구
- (2019-11-15) serial 및 socket 통합 지원

---

## Version Numbering

Format: `YYYY.MM.XXX`
- YYYY: Year
- MM: Month
- XXX: Sequential release number for the month

Example: 2025.01.010 = 10th release in January 2025