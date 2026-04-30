# 코콤 KE-20TEL + Elfin EW11 연동 가이드

## 월패드 정보

| 항목              | 값                      |
| --------------- | ---------------------- |
| **모델**          | 코콤 KE-20TEL            |
| **설치 아파트**      | 덕계역금강펜트리움              |
| **RS485 통신**    | 9600bps, 8N1           |
| **EW11 IP**     | 192.168.0.222          |
| **EW11 TCP 포트** | 8899                   |
| **EW11 웹 로그인**  | (설정 필요)                |
| **EW11 펌웨어**    | 1.44.1 (build23092615) |

## EW11 설정

### 현재 설정 (정상 동작 확인됨)

**Serial Port Settings:**

* Baud Rate: 9600

* Data Bit: 8

* Stop Bit: 1

* Parity: None

* Buffer Size: 512

* Gap Time: 50ms

**Communication Settings:**

* Protocol: TCP Server

* Local Port: 8899

* Buffer Size: 512

* Keep Alive: 60s

* Timeout: 0 (무제한)

* Max Accept: 20

* Route: Uart

### EW11 관리

* 웹 관리: `http://192.168.0.222` (기본 계정 사용)

* MAC: 74E9D83E2F54

* WiFi: Connected (RSSI 100)

### EW11 연결 문제 해결

**자주 끊기는 원인:**

1. **동시 연결 초과** - Max Accept 값이 낮으면 (기본 3) 여러 클라이언트가 접속 시 EW11이 먹통됨

   * 해결: Max Accept을 20으로 증가
2. **HA 애드온 + 테스트 스크립트 동시 접속** - 소켓이 제대로 종료되지 않으면 연결 슬롯 소진
3. **전원 불안정** - EW11 전원 어댑터 확인
4. **WiFi 신호** - 공유기와 거리/장애물 확인

**EW11 상태 확인:**

```bash
# Ping 테스트
ping 192.168.0.222

# TCP 포트 확인
nc -zv 192.168.0.222 8899

# 웹 상태 페이지
curl -u "USERNAME:PASSWORD" http://192.168.0.222/
```

## RS485 프로토콜 분석

### 패킷 구조 (21 바이트)

```
aa55 | type(2) | seq(1) | mon(1) | dest(2) | src(2) | cmd(1) | value(8) | chksum(1) | 0d0d
```

| 필드       | 위치 (hex) | 설명                                 |
| -------- | -------- | ---------------------------------- |
| Header   | \[0:4]   | `aa55` 고정                          |
| Type     | \[4:7]   | `30b`=send, `30d`=ack              |
| Seq      | \[7:8]   | `c`=1st, `d`=2nd, `e`=3rd, `f`=4th |
| Monitor  | \[8:10]  | `00`=wallpad                       |
| Dest     | \[10:14] | 목적지 디바이스                           |
| Src      | \[14:18] | 출발지 디바이스                           |
| Cmd      | \[18:20] | 명령 코드                              |
| Value    | \[20:36] | 8바이트 데이터                           |
| Checksum | \[36:38] | SUM % 256 (hex\[4:36])             |
| Trailer  | \[38:42] | `0d0d` 고정                          |

### 표준 코콤 디바이스 코드

| 코드   | 디바이스     | 비고    |
| ---- | -------- | ----- |
| `01` | wallpad  | 월패드   |
| `0e` | light    | 조명    |
| `2c` | gas      | 가스    |
| `36` | thermo   | 온도조절기 |
| `39` | ac       | 에어컨   |
| `3b` | plug     | 콘센트   |
| `44` | elevator | 엘리베이터 |
| `48` | fan      | 환기    |

### 이 아파트에서 발견된 비표준 디바이스

| 코드   | 추정      | 응답 여부       | 비고                   |
| ---- | ------- | ----------- | -------------------- |
| `53` | 미확인     | query 응답 없음 | 월패드가 주기적으로 query     |
| `54` | 조명 컨트롤러 | 조명 상태 수신처   | 조��(0e)이 상태를 보고하는 대상 |
| `73` | 미확인     | query 응답 없음 | 월패드가 주기적으로 query     |
| `82` | 미확인     | query 응답 있음 | cmd=01에 val=ff... 응답 |

### 명령 코드

| 코드   | 명령    | 설명       |
| ---- | ----- | -------- |
| `00` | state | 상태 조회/설정 |
| `01` | on    | 켜기       |
| `02` | off   | 끄기       |
| `3a` | query | 상태 질의    |

## 조명 상태 패킷 분석

### 캡처된 패킷 (월패드에서 조명 조작 시)

```
조명 ON:  0e00 → 5400  cmd=00  val=ff00000000000000
조명 OFF: 0e00 → 5400  cmd=00  val=0000000000000000
```

* 조명(0e00)이 컨트롤러(5400)에 **상태만 브로드캐스트**

* 월패드(0100)에서 조명(0e00)으로 가는 **명령 패킷은 RS485 버스에 없음**

* 각 상태 변경 시 3회 반복 전송 (seq c, d, e)

### Value 필드 (조명 상태)

```
byte 0: 조명 1 (ff=ON, 00=OFF)
byte 1: 조명 2
byte 2: 조명 3
byte 3: 조명 4
byte 4-7: 미사용 (00)
```

### 주기적 폴링 패킷

```
0100 → 5300  cmd=3a  (응답 없음)
0100 → 7300  cmd=3a  (응답 없음)
0100 → 8200  cmd=3a  (응답 있음: ACK)
```

월패드가 \~10초 간격으로 53, 73, 82 디바이스를 폴링합니다.

## 조명 제어 ���도 결과

### 시도한 패킷 조합 (모두 실패)

| # | Dest | Src  | Cmd         | 응답 | 조명 동작 |
| - | ---- | ---- | ----------- | -- | ----- |
| A | 0e00 | 5400 | 00 (state)  | O  | ❌     |
| B | 0e00 | 0100 | 00 (state)  | X  | ❌     |
| C | 0e00 | 0100 | 01 (on)     | X  | ❌     |
| D | 8200 | 0100 | 01 (on)     | O  | ❌     |
| E | 0e00 | 5400 | 01 (on)     | O  | ❌     |
| F | 5400 | 0100 | 00 (state)  | O  | ❌     |
| G | 5400 | 0100 | 01 (on)     | O  | ❌     |
| H | 5400 | 0e00 | 00 (state)  | X  | ❌     |
| I | 0e00 | 5400 | 00 (val=01) | O  | ❌     |
| J | 8200 | 0100 | 00 (state)  | O  | ❌     |

### 결론

**이 아파트의 RS485 버스는 조명 상태 모니터링만 가능합니다.**

* ✅ 조명 상태 읽기 (ON/OFF 모니터링)

* ❌ 조명 제어 (ON/OFF 명령)

월패드가 조명을 제어하는 경로는 이 RS485 버스가 아닌 것으로 판단됩니다.

## 가능한 원인 및 해결 방안

### 원인 1: RS485 포트가 2개로 분리

일부 코콤 아파트는 **조명/난방이 별도 RS485 버스**로 분리되어 있습니다.

* 현재 EW11은 **상태 보고용 버스**에만 연결된 상태

* 월패드 뒷면에 별도의 RS485 포트가 있을 수 있음

**확인 방법:** 월패드 뒷면을 열어서 RS485 포트가 여러 개인지 확인

### 원인 2: 서브폰 연결

* EW11을 서브폰 포트에 연결한 경우, 모든 RS485 신호가 전달되지 않을 수 있음

* 월패드 메인 보드의 RS485 포트에 직접 연결해야 할 수 있음

### 원인 3: 다른 통신 방식

* 최신 코콤 월패드는 RS485 외에 다른 통신 (TCP/IP, Zigbee 등)을 사용할 수 있음

### 해결 방안

1. **월패드 뒷면 RS485 포트 확인** - 별도 조명 제어용 포트가 있는지 확인
2. **EW11 연결 위치 변경** - 다른 RS485 포트에 연결 시도
3. **조명은 모니터링만** - 제어 불가 시 상태 모니터링만 활용
4. **다른 디바이스 집중** - thermo, elevator 등 제어 가능한 디바이스 우선 연동

## kocom.py 설정

### kocom.conf 주요 설정

```ini
[RS485]
type = socket
socket_server = 192.168.0.222
socket_port = 8899

[MQTT]
mqtt_server = core-mosquitto
mqtt_port = 1883
mqtt_username = YOUR_USERNAME
mqtt_password = YOUR_PASSWORD

[Device]
enabled = elevator, light_livingroom, light_room1, light_room2, light_room3, light_kitchen, thermo_livingroom, thermo_room1, thermo_room2, thermo_room3
light_controller = 5400

[Elevator]
type = rs485
rs485_floor = 15
```

### HA 애드온 설정

```yaml
rs485_type: socket
socket_server: 192.168.0.222
socket_port: 8899
mqtt_server: core-mosquitto
mqtt_port: 1883
mqtt_username: YOUR_USERNAME
mqtt_password: YOUR_PASSWORD
mqtt_allow_anonymous: false
elevator_floor: 15
init_temp: 23
debug_mode: true
```

## 참고 자료

* [코콤 월패드 RS485 패킷 캡처하기](https://blog.oriang.net/22)

* [서브폰에 EW11 연결하기](https://blog.oriang.net/45)

* [Home Assistant + 코콤 연동하기](https://blog.oriang.net/24)

* [코콤 월패드 RS485 H/W 연동](https://www.kimnjang.com/98)

* [RS485 패킷 분석 준비](https://jihunroh.github.io/2020/10/03/%EC%9B%94%ED%8C%A8%EB%93%9C-%EC%9B%90%EA%B2%A9%EC%A0%9C%EC%96%B4%EB%A5%BC-%EC%9C%84%ED%95%9C-RS485-%ED%8C%A8%ED%82%B7-%EB%B6%84%EC%84%9D-%EC%A4%80%EB%B9%84/)

* [HomeAssistant 코콤 연동](https://blog.djjproject.com/646)

* [코콤 월패드 RS485 패킷 분석](https://mscg.kr/65)

* [kocomRS485 GitHub](https://github.com/zooil/kocomRS485)

* [iquix/kocom.py GitHub](https://github.com/iquix/kocom.py)

* [GuGu927/RS485 GitHub](https://github.com/GuGu927/RS485)

* [코콤 공식 사이트](https://www.kocom.co.kr/)
