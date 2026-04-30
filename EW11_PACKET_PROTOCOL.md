# EW11 RS485 패킷 프로토콜 분석

덕계역금강펜트리움 - kocom.py 로직 기반 프로토콜 문서

## 패킷 구조 (21 bytes)

```
aa55 | 30b/30d | seq | 00 | dest(2) | src(2) | cmd | value(8) | chksum | 0d0d
 (2)     (3)     (1)  (2)    (4)       (4)     (2)    (16)       (2)      (2)
header  type    seq  mon   device    device   cmd    payload   check   trailer
```

### 필드 설명

| 필드 | 크기 | 설명 | 예시 |
|------|------|------|------|
| header | 4 | 고정 헤더 | `aa55` |
| type | 3 | 패킷 타입 | `30b`(CMD), `30d`(ACK), `309`(BATCH) |
| seq | 1 | 시퀀스 코드 | `c`, `d`, `e`, `f` |
| monitor | 2 | 모니터 코드 | `00` (일반적으로 사용 안함) |
| dest | 4 | 목적지 장치 | `0e00`(거실 조명) |
| src | 4 | 출발지 장치 | `0100`(월패드) |
| cmd | 2 | 명령 코드 | `01`(ON), `02`(OFF), `3a`(QUERY) |
| value | 16 | 데이터 페이로드 | 조명: `ff00000000000000` (1번 ON) |
| checksum | 2 | 체크섬 | 페이로드 합계 % 256 |
| trailer | 4 | 고정 트레일러 | `0d0d` |

## 장치 코드 (device_h_dic)

| 코드 | 장치 | 설명 |
|------|------|------|
| `01` | wallpad | 월패드 (제어 주체) |
| `0e` | light | 조명 |
| `2c` | gas | 가스차단기 |
| `36` | thermo | 온도조절기 |
| `39` | ac | 에어컨 |
| `3b` | plug | 콘센트 |
| `44` | elevator | 엘리베이터 |
| `48` | fan | 환기장치 |
| `54` | batch | 일괄스위치 |

## 방 코드 (room_h_dic)

| 코드 | 방 이름 | 한글 |
|------|---------|------|
| `00` | livingroom | 거실 |
| `01` | master | 안방 |
| `02` | office | 작업실 |
| `03` | guest | 손님방 |

## 명령 코드 (cmd_h_dic)

| 코드 | 명령 | 설명 |
|------|------|------|
| `00` | state | 상태 보고 |
| `01` | on | 켜기 |
| `02` | off | 끄기 |
| `3a` | query | 상태 조회 |
| `65` | batch_on | 일괄소등 활성화 |
| `66` | batch_off | 일괄소등 해제 |

## 패킷 타입

| 타입 | 이름 | 방향 | 설명 |
|------|------|------|------|
| `30b` | COMMAND | 월패드 → 장치 | 제어 명령 |
| `30d` | ACK | 장치 → 월패드 | 명령 응답 (성공) |
| `309` | BATCH | 월패드 → 일괄 | 일괄소등 제어 |

## kocom.py 조명 제어 로직

### 1. 현재 상태 조회 (query)

```python
value = query(dev_id)['value']
# dev_id 예: 0e00 (거실 조명)
# 반환값 예: {'value': 'ff00000000000000'} - 1번 조명만 켜져있음
```

**Query 패킷 생성** (kocom.py:269):
```python
payload = '30b' + seq_h + '00' + dest + src + '3a' + '0'*16
# 예: 30bc000e0001003a00000000000000000d0d
```

### 2. 값 수정

```python
onoff_hex = 'ff' if command == 'on' else '00'
light_id = int(topic_d[3])  # 조명 번호 (1-4)
n = light_id
value = value[:n*2-2] + onoff_hex + value[n*2:]
```

**예시**: 2번 조명 켜기
- 현재 상태: `ff00000000000000` (1번만 ON)
- light_id = 2, n = 2
- value[:2] + 'ff' + value[4:] = `ff` + `ff` + `000000000000`
- 결과: `ffff000000000000` (1,2번 ON)

### 3. 명령 전송 (send)

```python
send_wait_response(dest=dev_id, src=light_controller_addr, value=value, log='light')
```

**Command 패킷 생성** (kocom.py:269-270):
```python
for seq_h in ['c', 'd', 'e', 'f']:  # ACK 없으면 재시도
    payload = '30b' + seq_h + '00' + dest + src + cmd + value
    send_data = 'aa55' + payload + chksum(payload) + '0d0d'
    rs485.write(bytearray.fromhex(send_data))
```

**예시 패킷**: 거실 2번 조명 켜기
```
aa55 30bc 00 0e00 0100 01 ffff000000000000 XX 0d0d
     CMD  seq dest src  ON    1,2번 ON     chk
```

### 4. ACK 대기

**예상 ACK 패킷** (kocom.py:285):
```python
ack_data.append('30d' + seq_h + '00' + src + dest + cmd + value)
# 30dc000100 0e00 01 ffff000000000000
```

타임아웃: 1.3~1.5초 (random)

### 5. 일괄소등 해제 (덕계역금강펜트리움 전용)

조명 제어 후 자동으로 일괄소등이 활성화되는 문제 방지:

```python
send_batch_off_continuous(duration=5)
# 5초간 batch-off 패킷 연속 전송
```

**Batch OFF 패킷**:
```
aa55 309c 00 0eff 0100 66 ffffffffffffffff XX 0d0d
     BATCH    전체  월패 OFF  모두 ON       chk
```

## 체크섬 계산

```python
def chksum(data_h):
    return '{0:02x}'.format(sum(bytearray.fromhex(data_h)) % 256)

# 예: payload = '30bc000e0001003a0000000000000000'
# sum = 0x30+0xb+0xc+0x0+...
# checksum = sum % 256
```

## 시퀀스 재시도 로직

kocom.py는 ACK를 받지 못하면 시퀀스 코드를 변경하여 최대 4번 재시도:

```python
seq_t_dic = {'c': 'seq1', 'd': 'seq2', 'e': 'seq3', 'f': 'seq4'}

for seq_h in ['c', 'd', 'e', 'f']:
    send_packet_with_seq(seq_h)
    wait_for_ack(timeout=1.3~1.5)
    if ack_received:
        break
```

## 패킷 파싱 (recv)

```python
def parse(data_h):
    return {
        'header': data_h[:4],         # aa55
        'type': data_h[4:7],          # 30b/30d/309
        'seq': data_h[7:8],           # c/d/e/f
        'monitor': data_h[8:10],      # 00
        'dest': data_h[10:14],        # 0e00
        'src': data_h[14:18],         # 0100
        'cmd': data_h[18:20],         # 01/02/3a
        'value': data_h[20:36],       # payload (16 chars)
        'chksum': data_h[36:38],      # checksum
        'trailer': data_h[38:42]      # 0d0d
    }
```

## 실제 패킷 예시

### 거실 1번 조명 켜기

1. **Query** (월패드 → 조명):
   ```
   aa55 30bc 00 0e00 0100 3a 0000000000000000 XX 0d0d
   ```

2. **Query Response** (조명 → 월패드):
   ```
   aa55 30dc 00 0100 0e00 3a 0000000000000000 XX 0d0d
   현재 모두 꺼져있음 ─────┘
   ```

3. **ON Command** (월패드 → 조명):
   ```
   aa55 30bc 00 0e00 0100 01 ff00000000000000 XX 0d0d
   1번만 켬 ──────────────┘
   ```

4. **ACK** (조명 → 월패드):
   ```
   aa55 30dc 00 0100 0e00 01 ff00000000000000 XX 0d0d
   성공 ──────────────────┘
   ```

5. **Batch OFF** (월패드 → 일괄):
   ```
   aa55 309c 00 0eff 0100 66 ffffffffffffffff XX 0d0d
   (5초간 0.3초 간격 반복)
   ```

## 일괄소등 프로토콜 (덕계역금강펜트리움)

### 일괄소등 ON (모든 조명 끄기)
```
aa55 309c 00 0eff 0100 65 0000000000000000 3f 0d0d
     BATCH    전체  월패 ON   모두 OFF
```

### 일괄소등 OFF (해제)
```
aa55 309c 00 0eff 0100 66 ffffffffffffffff 38 0d0d
     BATCH    전체  월패 OFF  모두 ON
```

**특이사항**:
- 타입이 `309c`로 일반 명령(`30bc`)과 다름
- cmd=65(ON)일 때 value는 00...(끔 상태)
- cmd=66(OFF)일 때 value는 ff...(켬 상태)
- 반대 논리로 작동

## kocom.py 핵심 함수

### send()
**위치**: kocom.py:264
**역할**: 패킷 생성 및 전송, ACK 대기
```python
def send(dest, src, cmd, value, log=None, check_ack=True):
    for seq_h in ['c', 'd', 'e', 'f']:
        payload = '30b' + seq_h + '00' + dest + src + cmd + value
        send_data = 'aa55' + payload + chksum(payload) + '0d0d'
        rs485.write(bytearray.fromhex(send_data))
        if wait_for_ack(timeout=1.5):
            break
```

### send_wait_response()
**위치**: kocom.py:430
**역할**: send() 호출 + 응답 대기 + MQTT 발행
```python
def send_wait_response(dest, src='0100', cmd='00', value='0'*16, log=None):
    send(dest, src, cmd, value, log)
    return wait_q.get(timeout=2)  # ACK + 상태 패킷 대기
```

### query()
**위치**: kocom.py:408
**역할**: 장치 상태 조회 (캐시 우선)
```python
def query(device_h):
    # 캐시 확인
    for c in cache_data:
        if c['dest_h'] == device_h and c['type'] == 'ack':
            return c  # 캐시된 상태 반환
    # 캐시 없으면 query 패킷 전송
    return send_wait_response(dest=device_h, cmd='3a')
```

### parse()
**위치**: kocom.py:354
**역할**: 수신 패킷을 딕셔너리로 파싱
```python
def parse(data_h):
    return {
        'type': data_h[4:7],
        'dest': data_h[10:14],
        'src': data_h[14:18],
        'cmd': data_h[18:20],
        'value': data_h[20:36],
        # ... 생략
    }
```

## 디버깅 팁

### 1. 패킷 로깅 활성화
```ini
[Log]
show_query_hex = True
show_recv_hex = True
show_mqtt_publish = True
```

### 2. 체크섬 검증
```python
def verify_packet(hex_str):
    payload = hex_str[4:36]  # header 이후, checksum 이전
    expected = chksum(payload)
    actual = hex_str[36:38]
    return expected == actual
```

### 3. 패킷 방향 확인
- `src='01xx'` → 월패드가 보낸 패킷 (명령)
- `dest='01xx'` → 월패드가 받을 패킷 (응답)

### 4. 캡처할 패킷 유형
- ✅ `30bc` + src=`01xx` → **명령 패킷** (재전송 가능)
- ❌ `30dc` + dest=`01xx` → 응답 패킷 (재전송 불가)

## 참고 자료

- kocom.py 소스: `/Users/robert/Develop/dev2025/kocom.py/kocom.py`
- 설정 파일: `/share/kocom/kocom.conf`
- CLAUDE.md: 프로젝트 개요 및 가이드
- CHANGELOG.md: 변경 이력 및 일괄소등 문제 해결 과정
