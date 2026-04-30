# Kocom Light Interactive Test Tool

JSON 설정 기반 대화형 조명 테스트 프로그램

## 특징

- `packets.json`과 `protocol.json` 설정 자동 로드
- 실시간 조명 제어 테스트
- 일괄소등(batch-off) 패킷 전송 테스트
- 연속 batch-off 전송 테스트

## 사용법

### 1. 프로그램 실행

```bash
python3 test_light_interactive.py
```

### 2. 연결 정보 입력

```
Enter RS485 gateway IP [192.168.0.222]:
Enter RS485 gateway port [8899]:
```

기본값 사용 시 그냥 Enter

### 3. 명령어

#### 조명 켜기
```
>>> on <room_code> <light_num>
```

예시:
```
>>> on 00 1      # 거실(livingroom) 조명 1번 켜기
>>> on 01 2      # 안방(master) 조명 2번 켜기
```

#### 조명 끄기
```
>>> off <room_code> <light_num>
```

예시:
```
>>> off 00 1     # 거실 조명 1번 끄기
>>> off 02 3     # 작업실(office) 조명 3번 끄기
```

#### 일괄소등 해제 (단발)
```
>>> batch_off
```

#### 일괄소등 해제 (연속 전송)
```
>>> batch_cont <duration>
```

예시:
```
>>> batch_cont 5    # 5초간 연속 전송
>>> batch_cont 10   # 10초간 연속 전송
```

#### 기타 명령
```
>>> menu          # 메뉴 표시
>>> reconnect     # 재연결
>>> exit          # 종료
```

## 방 코드 (Room Codes)

| 코드 | 이름 | 한글 |
|------|------|------|
| 00 | livingroom | 거실 |
| 01 | master | 안방 |
| 02 | office | 작업실 |
| 03 | guest | 손님방 |
| 04 | kitchen | 주방 |

## 조명 번호

각 방마다 조명 1~4번까지 지원

## 사용 예시

```
Kocom Light Interactive Test Tool
============================================================

Enter RS485 gateway IP [192.168.0.222]:
Enter RS485 gateway port [8899]:
[CONNECT] Connected to 192.168.0.222:8899
[CONFIG] Loaded configuration from JSON files
  - Devices: ['wallpad', 'light', 'gas', 'thermo', 'ac', 'plug', 'elevator', 'fan', 'batch']
  - Rooms: ['livingroom', 'master', 'office', 'guest', 'kitchen']

>>> on 00 1
[LIGHT] Room: 00, Light: 1, Command: ON
  Dest: 0e00, Src: 5400, Cmd: 00, Value: ff00000000000000
[SEND] aa5530bc000e005400ff00000000000000XX0d0d
[OK] Light 1 in livingroom turned ON

>>> batch_cont 3
[BATCH_OFF_CONTINUOUS] Duration: 3s, Interval: 0.3s
  Progress: 5 packets sent
  Progress: 10 packets sent
[BATCH_OFF_CONTINUOUS] Complete - 10 packets sent
[OK] Batch-off continuous complete

>>> exit
[DISCONNECT] Disconnected from gateway
```

## 일괄소등 디버깅

조명 제어 후 일괄소등이 자동으로 활성화되는 문제를 테스트할 때:

1. 조명 켜기: `on 00 1`
2. 일괄소등 상태 확인 (월패드에서)
3. batch-off 전송: `batch_cont 5`
4. 일괄소등 해제 확인

## 주의사항

- 실제 RS485 통신이므로 월패드와 기기 상태가 실시간으로 변경됩니다
- 테스트 전 현재 조명 상태를 확인하세요
- EW11 연결이 안정적인지 확인하세요 (192.168.0.222:8899)

## 문제 해결

### 연결 실패
```
[ERROR] Connection failed: [Errno 61] Connection refused
```
- EW11 IP/포트 확인
- EW11 전원 및 WiFi 연결 확인
- 방화벽 설정 확인

### 패킷 전송 실패
```
[ERROR] Send failed: [Errno 32] Broken pipe
```
- `reconnect` 명령으로 재연결
- EW11 웹 페이지에서 연결 상태 확인 (http://192.168.0.222)

## 로그 확인

kocom.py 애드온 로그에서 `[BATCH_DEBUG]` 태그 검색:
- 조명 제어 패킷
- batch-off 전송 상태
- 309c 특수 패킷 감지
- batch device (54) 패킷
