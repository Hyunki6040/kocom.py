# 📝 CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2026.05.007] - 2026-05-01

### 🔧 Changed
- **Elevator entity type** - Changed from switch to button
  - Elevator has no "off" concept, only "call"
  - Button provides better UX - single press to call
  - Removed unnecessary state tracking (stat_t, val_tpl, pl_off)
  - Discovery: homeassistant/switch → homeassistant/button

---

## [2026.05.006] - 2026-05-01

### 🐛 Fixed
- **Critical startup error** - Fixed KeyError on `device_h_dic['wallpad']` at module load time
  - Changed `send_wait_response()` function signature to use `None` defaults
  - Default values now evaluated at function call time, not module load time
  - Prevents crash when JSON config not yet loaded
- **Missing JSON files** - Fixed run.sh to copy packets.json and protocol.json to /share/kocom/
  - Previously only kocom.py was copied, causing FileNotFoundError
  - Now all required files are deployed to runtime directory

### 🌐 Localization Update
- **English entity names** - All Home Assistant friendly_name fields now display in English
  - Fan (환풍기)
  - Gas Cutoff (가스 차단)
  - Elevator Call (엘리베이터 호출)
  - {Room} Light {Number} - 예: Livingroom Light 1
  - {Room} Thermostat - 예: Master Bedroom Thermostat
  - {Room} AC - 예: Livingroom AC
  - Query Status (상태 조회)
- **packets.json**: Added `room_names_english` mapping for proper entity naming
- Better compatibility with Home Assistant UI translation system

---

## [2026.05.005] - 2026-05-01

### 🧪 Testing Tools
- **Comprehensive test tool** - Expanded test_light_interactive.py to include all device types
  - 조명 (Light) - ON/OFF control
  - 난방 (Thermostat) - Heat ON/OFF with temperature setting (5-30°C)
  - 엘리베이터 (Elevator) - Call elevator
  - 환풍기 (Fan) - OFF/Low/Medium/High presets
  - 가스 (Gas) - Emergency cutoff
  - 일괄소등 (Batch) - Batch ON/OFF/Continuous OFF
- **Renamed class** - LightTester → WallpadTester for clarity
- **Interactive menus** - Intuitive submenus for all device controls
- **packets.json**: Added `batch_on` special packet configuration

---

## [2026.05.004] - 2026-05-01

### 🌐 Localization
- **Korean entity names** - All Home Assistant entities now display in Korean
  - 환풍기 (Fan)
  - 가스 차단 (Gas)
  - 엘리베이터 호출 (Elevator)
  - {방} 조명 {번호} (Light) - 예: 거실 조명 1
  - {방} 난방 (Thermostat) - 예: 안방 난방
  - {방} 에어컨 (AC) - 예: 거실 에어컨
  - 상태 조회 (Query)
- **packets.json**: Added `room_names_korean` mapping

---

## [2026.05.003] - 2026-05-01

### 🔧 Fixed
- **Corrected room light counts for 덕계역금강펜트리움**
  - 거실 (livingroom): 4 → 3 lights
  - 주방 (kitchen): 4 → 0 lights (no lights)
- **kocom.py**: Skip MQTT discovery for rooms with 0 lights
- **test_light_interactive.py**: Show "no lights" message for rooms with 0 lights

---

## [2026.05.002] - 2026-05-01

### 🏠 Customized for 덕계역금강펜트리움
- **Room-specific light configuration** - Different number of lights per room
  - 거실 (livingroom): 4 lights
  - 안방 (master): 2 lights
  - 작업실 (office): 1 light
  - 손님방 (guest): 1 light
  - 주방 (kitchen): 4 lights
- **packets.json**: Added `room_lights` configuration
- **kocom.py**: MQTT discovery and command validation based on room_lights
- **test_light_interactive.py**: Dynamic light selection menu based on room

---

## [2026.05.001] - 2026-05-01

### 🔧 Fixed
- **Thermostat minimum temperature** - Changed from 20°C to 5°C for proper heating control range
  - Previously restricted to 20-30°C range
  - Now allows full 5-30°C range for accurate temperature control

---

## [2026.04.005] - 2026-04-30

### 🐛 Debug
- **일괄소등 원인 파악을 위한 상세 로깅 추가**
  - 조명 제어 시 모든 패킷 로깅 (`[BATCH_DEBUG]` 태그)
  - batch_off_continuous() 전송 상태 및 진행 상황 로깅
  - 특수 패킷 타입 309c 감지 로깅
  - batch device (54) 패킷 감지 및 상세 정보 로깅
  - batch 명령(65/66) 감지 로깅
- 일괄소등이 자동으로 활성화되는 원인 추적 가능

---

## [2026.04.004] - 2026-04-30

### 🐛 Fixed
- **Critical Dockerfile fix** - Added missing JSON configuration files (packets.json, protocol.json) to Docker image
- Without these files, the addon would fail to start with "Failed to load" errors

---

## [2026.04.003] - 2026-04-30

### 🏗️ Refactored
- **JSON-based configuration** - Extracted all packet data and protocol values to separate JSON files
  - Created `packets.json` - Device codes, commands, rooms, parsing configs, special packets
  - Created `protocol.json` - Timing parameters, packet structure, sequence codes
  - kocom.py now loads configuration dynamically via `load_json_config()`
- **Removed hardcoded values** - All device codes, parsing logic, and protocol parameters now managed via JSON
- **Improved maintainability** - Easy customization for different apartment complexes
- **Security** - Removed exposed credentials from all files (public repo safety)

### 🗑️ Removed
- **Air quality sensor** - Removed device code 98 (air) - not supported in any public Kocom source

---

## [2026.04.002] - 2026-04-30

### 🐛 Fixed
- **Disable light polling** - 조명 상태 조회(poll_state)가 일괄소등을 트리거하는 문제 해결
- `no_polling_list`에 'light' 추가하여 조명 폴링 비활성화

---

## [2026.04.001] - 2026-04-30

### ✨ Added
- **Room mapping for 덕계역금강펜트리움** - Updated room codes with Korean names (거실, 안방, 작업실, 손님방)
- **Batch switch protocol** - Documented `309c` packet type for 일괄소등 (cmd 65/66)
- **Device code 54** - Added batch switch device type

### 📝 Changed
- `room_t_dic` now uses descriptive names: livingroom, master, office, guest
- `room_h_dic` supports Korean room names (거실, 안방, 작업실, 손님방)
- `cmd_t_dic` includes batch_on (65) and batch_off (66) commands

---

## [2025.01.016] - 2025-04-25

### ✨ Added
- **Custom light controller address** - `light_controller` config option for apartments with non-standard controller addresses (e.g., 덕계역금강펜트리움 uses 5400 instead of standard 0100)

### 📝 Changed
- Light control commands now use configurable controller address as source
- Light queries also use the configured controller address for compatibility

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