# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kocom Wallpad RS485 integration for Home Assistant. A Home Assistant add-on that communicates with Kocom wallpad devices via RS485 serial or socket connection and bridges them to Home Assistant through MQTT.

**Target Environment**: 덕계역금강펜트리움 apartment complex

## Architecture

### Communication Flow
```
Kocom Wallpad <--RS485--> kocom.py <--MQTT--> Home Assistant
```

### Key Components

**kocom.py** - Single-file application (~1000 lines) containing:
- `RS485Wrapper` class: Manages serial/socket communication with reconnect logic
- MQTT client: paho-mqtt 2.x with callback API v2
- Packet parser: Translates 21-byte hex packets to/from device states
- MQTT Discovery: Auto-registers devices with Home Assistant

### RS485 Protocol

**Packet Structure** (21 bytes):
```
aa55 | 30b/30d | seq | 00 | dest(2) | src(2) | cmd | value(8) | chksum | 0d0d
header  type     seq  mon   device    device  cmd    payload    check   trailer
```

**Device Codes** (`device_t_dic`):
- `01`: wallpad, `0e`: light, `2c`: gas, `36`: thermo
- `39`: ac, `3b`: plug, `44`: elevator, `48`: fan, `54`: batch (일괄소등)

**Command Codes** (`cmd_t_dic`):
- `00`: state, `01`: on, `02`: off, `3a`: query
- `65`: batch_on (일괄소등 활성화), `66`: batch_off (일괄소등 해제)

**Room Codes** (`room_t_dic`) - 덕계역금강펜트리움:
- `00`: livingroom (거실)
- `01`: master (안방)
- `02`: office (작업실)
- `03`: guest (손님방)
- `04`: kitchen (주방) - 미지원

### Batch Switch (일괄소등) Protocol

Special packet type `309c` for batch switch control:
```
일괄소등 ON:  aa55309c000eff01006500000000000000003f0d0d
일괄소등 OFF: aa55309c000eff010066ffffffffffffffff380d0d
```
- Type: `309c` (special, not standard `30bc`)
- Dest: `0eff` (all lights)
- Cmd: `65` (batch on), `66` (batch off)
- Value: `00...` (all off), `ff...` (all on)

### Data Flow

1. **Inbound (RS485 → MQTT)**: `recv_worker()` thread reads packets → `parse()` → `publish_status()` → MQTT publish
2. **Outbound (MQTT → RS485)**: `mqtt_on_message()` → `send_wait_response()` → RS485 write with ACK wait

### Threading Model
- Main thread: Initialization and polling timer
- `recv_worker`: Continuous RS485 read loop
- `packet_processor`: Async MQTT publishing
- `poll_state`: Periodic device state queries (300s default)

## Build and Run

```bash
# Build Docker image
docker build -t kocom-wallpad .

# Run container
docker run -v /path/to/share:/share kocom-wallpad

# Monitor MQTT messages
mosquitto_sub -h [mqtt_server] -p 1883 -t 'kocom/#' -v
```

## Configuration

Configuration is read from `/data/options.json` (HA addon UI) with fallback to `/share/kocom/kocom.conf`.

### Key Config Sections
- **[RS485]**: `type` (serial/socket), connection details
- **[MQTT]**: Server, port, authentication
- **[Device]**: `enabled` - comma-separated list (e.g., `elevator, light_livingroom, thermo_room1`)
- **[Elevator]**: `type` (rs485/tcpip), `rs485_floor`
- **[Log]**: Debug flags (`show_query_hex`, `show_recv_hex`, `show_mqtt_publish`)

## MQTT Topics

**Command**: `kocom/{room}/{device}/command` or `kocom/{room}/{device}/{subcommand}/command`
**State**: `kocom/{room}/{device}/state`
**Discovery**: `homeassistant/{component}/kocom_{id}/config`

## Adding New Device Types

1. Add device code to `device_t_dic` and reverse `device_h_dic`
2. Create parse function (e.g., `new_device_parse(value)`) to decode packet value
3. Add MQTT command handler in `mqtt_on_message()`
4. Add state publisher case in `packet_processor()`
5. Add discovery payload in `publish_discovery()`

## Debug RS485 Communication

Enable in kocom.conf:
```ini
show_query_hex = True
show_recv_hex = True
```

Check logs for hex packet dumps and verify checksum calculations using `chksum()` function.

## EW11 Connection (덕계역금강펜트리움)

- **IP**: 192.168.0.222
- **Port**: 8899
- **Serial**: 9600-8-N-1

## Important Notes

- Elevator TCP/IP mode is experimental - requires capturing apartment server packets
- Polling interval default is 300 seconds
- ACK wait timeout is 1.3-1.5 seconds with random jitter
- `read_write_gap` (30ms) prevents RS485 collision
- **일괄소등 Issue (SOLVED)**: Light commands trigger batch switch ON. Solution: Send batch-off packet continuously for 5 seconds after each light command. See `send_batch_off_continuous()` in kocom.py

## Lessons Learned (2025-04-30)

### 일괄소등 (Batch Switch) 디버깅

**문제**: 조명 제어 시 자동으로 일괄소등이 활성화되어 모든 조명이 꺼짐

**디버깅 과정**:
1. 일괄소등 패킷 캡처 → `309c` 타입 발견 (일반 `30bc`와 다름)
2. 단일 batch-off 전송 시도 → 실패 (일시적으로 해제되었다가 다시 ON)
3. 다양한 src 주소 시도 (0e00, 5400, 0100) → 일관성 없음
4. 연속 전송 시도 (5초간 17회) → **성공**

**핵심 발견**:
- 월패드는 조명 명령 후 일괄소등을 자동 활성화하는 내부 로직 존재
- 단일 batch-off로는 이 로직을 "이길" 수 없음
- 연속 전송으로 월패드의 재활성화 시도를 압도해야 함

**최종 해결책**:
```python
def send_batch_off_continuous(duration=5):
    end_time = time.time() + duration
    while time.time() < end_time:
        rs485.write(bytearray.fromhex(BATCH_OFF_PACKET))
        time.sleep(0.3)
```

**패킷 분석**:
```
309c 타입: 일괄소등 전용
- cmd=65: batch ON (모든 조명 끔)
- cmd=66: batch OFF (일괄소등 해제)
- dest=0eff: 전체 조명
- value=00...: 상태값 (00=off, ff=on)
```

## Version Management

- Update `SW_VERSION` in kocom.py
- Update `version` in config.yaml
- Update CHANGELOG.md with today's date for major changes only
