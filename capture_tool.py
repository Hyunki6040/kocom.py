#!/usr/bin/env python3
"""
Kocom Wallpad ON/OFF Paired Packet Capture Tool
Captures ON and OFF packets together for each device
"""

import socket
import json
import time
import sys
import os
from datetime import datetime
from collections import Counter

class PairedPacketCapture:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.captured_devices = {}
        self.sock = None
        self.capture_file = "captured_devices.json"
        
    def connect(self):
        """Connect to EW11"""
        print(f"\n📡 EW11 연결 중... {self.server_ip}:{self.server_port}")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.1)
            self.sock.connect((self.server_ip, self.server_port))
            print("✅ 연결 성공!\n")
            return True
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False
    
    def collect_packets(self, duration):
        """Collect all packets for given duration"""
        packets = []
        buffer = ""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                data = self.sock.recv(4096)
                if data:
                    hex_data = data.hex()
                    buffer += hex_data
                    
                    # Extract complete packets
                    while 'aa55' in buffer and '0d0d' in buffer:
                        try:
                            start_pos = buffer.index('aa55')
                            end_pos = buffer.index('0d0d', start_pos) + 4
                            
                            if end_pos > start_pos:
                                packet = buffer[start_pos:end_pos]
                                buffer = buffer[end_pos:]
                                formatted = ' '.join([packet[i:i+2] for i in range(0, len(packet), 2)])
                                packets.append(formatted.upper())
                        except ValueError:
                            break
            except socket.timeout:
                continue
            except Exception:
                continue
        
        return packets
    
    def find_new_packets(self, baseline, action):
        """Find packets that appear in action but not in baseline"""
        baseline_counter = Counter(baseline)
        action_counter = Counter(action)
        
        new_packets = []
        for packet, count in action_counter.items():
            if packet not in baseline_counter or count > baseline_counter[packet]:
                new_packets.append(packet)
        
        return new_packets
    
    def capture_on_off_pair(self, device_name):
        """Capture ON and OFF packets for a device"""
        print("\n" + "="*70)
        print(f"🎯 장치: {device_name}")
        print("="*70)
        
        print(f"\n📌 '{device_name}' 캡처 순서: ON → OFF → ON → OFF")
        print("각 단계에서 안내에 따라 버튼을 1번만 누르세요.\n")
        
        results = {
            'ON': [],
            'OFF': []
        }
        
        # Step 1: Baseline
        print("[준비] 기준선 캡처 - 아무 버튼도 누르지 마세요")
        input("준비되면 Enter... ")
        print("⏱️  캡처 중... (5초)")
        baseline = self.collect_packets(5)
        print(f"✅ 기준선: {len(baseline)}개 패킷\n")
        
        time.sleep(2)
        
        # Step 2: First ON
        print("[1/4] 첫 번째 ON - 버튼을 눌러 켜세요")
        input("준비되면 Enter... ")
        print("⏱️  캡처 중... (5초 내에 ON 버튼)")
        on1_packets = self.collect_packets(5)
        on1_new = self.find_new_packets(baseline, on1_packets)
        if on1_new:
            print(f"✅ ON 패킷 후보: {len(on1_new)}개 발견")
            results['ON'].extend(on1_new)
        else:
            print("⚠️  새 패킷 없음")
        
        time.sleep(3)
        
        # Step 3: First OFF
        print("\n[2/4] 첫 번째 OFF - 버튼을 눌러 끄세요")
        input("준비되면 Enter... ")
        print("⏱️  캡처 중... (5초 내에 OFF 버튼)")
        
        # Get new baseline (with light ON)
        baseline_on = self.collect_packets(2)
        off1_packets = self.collect_packets(5)
        off1_new = self.find_new_packets(baseline_on, off1_packets)
        if off1_new:
            print(f"✅ OFF 패킷 후보: {len(off1_new)}개 발견")
            results['OFF'].extend(off1_new)
        else:
            print("⚠️  새 패킷 없음")
        
        time.sleep(3)
        
        # Step 4: Second ON (verification)
        print("\n[3/4] 두 번째 ON - 다시 켜세요 (검증)")
        input("준비되면 Enter... ")
        print("⏱️  캡처 중... (5초 내에 ON 버튼)")
        
        baseline_off = self.collect_packets(2)
        on2_packets = self.collect_packets(5)
        on2_new = self.find_new_packets(baseline_off, on2_packets)
        if on2_new:
            print(f"✅ ON 패킷 후보: {len(on2_new)}개 발견")
            results['ON'].extend(on2_new)
        else:
            print("⚠️  새 패킷 없음")
        
        time.sleep(3)
        
        # Step 5: Second OFF (verification)
        print("\n[4/4] 두 번째 OFF - 다시 끄세요 (검증)")
        input("준비되면 Enter... ")
        print("⏱️  캡처 중... (5초 내에 OFF 버튼)")
        
        baseline_on2 = self.collect_packets(2)
        off2_packets = self.collect_packets(5)
        off2_new = self.find_new_packets(baseline_on2, off2_packets)
        if off2_new:
            print(f"✅ OFF 패킷 후보: {len(off2_new)}개 발견")
            results['OFF'].extend(off2_new)
        else:
            print("⚠️  새 패킷 없음")
        
        # Analyze results
        print("\n" + "-"*70)
        print("📊 분석 결과:")
        
        # Find most common packets
        on_counter = Counter(results['ON'])
        off_counter = Counter(results['OFF'])
        
        final_on = None
        final_off = None
        
        if on_counter:
            # Get most common ON packet
            on_most_common = on_counter.most_common(3)
            print(f"\nON 패킷 후보:")
            for i, (packet, count) in enumerate(on_most_common, 1):
                print(f"  {i}. [{count}회] {packet}")
                self.show_packet_info(packet)
            
            if on_most_common[0][1] >= 2:  # Appeared at least twice
                final_on = on_most_common[0][0]
        
        if off_counter:
            # Get most common OFF packet
            off_most_common = off_counter.most_common(3)
            print(f"\nOFF 패킷 후보:")
            for i, (packet, count) in enumerate(off_most_common, 1):
                print(f"  {i}. [{count}회] {packet}")
                self.show_packet_info(packet)
            
            if off_most_common[0][1] >= 2:  # Appeared at least twice
                final_off = off_most_common[0][0]
        
        # Save if both found
        if final_on and final_off:
            print(f"\n✅ 성공! '{device_name}'의 ON/OFF 패킷 쌍을 찾았습니다.")
            print(f"  ON : {final_on}")
            print(f"  OFF: {final_off}")
            
            self.captured_devices[device_name] = {
                'ON': final_on,
                'OFF': final_off,
                'captured_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.save_devices()
            return True
        else:
            print(f"\n⚠️ 패킷 캡처 불완전:")
            if not final_on:
                print("  - ON 패킷을 찾지 못했습니다")
            if not final_off:
                print("  - OFF 패킷을 찾지 못했습니다")
            
            retry = input("\n다시 시도하시겠습니까? (y/n): ").strip().lower()
            if retry == 'y':
                return self.capture_on_off_pair(device_name)
            return False
    
    def show_packet_info(self, packet):
        """Display packet structure"""
        parts = packet.split()
        if len(parts) >= 10 and parts[0] == 'AA' and parts[1] == '55':
            device_map = {
                '00 0E': '조명',
                '00 36': '온도조절기',
                '00 2C': '가스',
                '00 44': '엘리베이터',
                '00 48': '환기'
            }
            device = ' '.join(parts[4:6])
            device_name = device_map.get(device, f"Unknown({device})")
            cmd = parts[7] if len(parts) > 7 else '??'
            room = parts[6] if len(parts) > 6 else '??'
            print(f"       → {device_name} | 방:{room} | 명령:{cmd}")
    
    def save_devices(self):
        """Save captured devices to file"""
        with open(self.capture_file, 'w') as f:
            json.dump(self.captured_devices, f, indent=2, ensure_ascii=False)
        print(f"💾 저장됨: {self.capture_file}")
    
    def load_devices(self):
        """Load previously captured devices"""
        if os.path.exists(self.capture_file):
            with open(self.capture_file, 'r') as f:
                self.captured_devices = json.load(f)
            count = len(self.captured_devices)
            if count > 0:
                print(f"📂 기존 장치 {count}개 불러옴")
    
    def show_devices(self):
        """Show all captured devices"""
        if not self.captured_devices:
            print("\n캡처된 장치가 없습니다.")
            return
        
        print("\n" + "="*70)
        print("📋 캡처된 장치 목록")
        print("="*70)
        for i, (name, data) in enumerate(self.captured_devices.items(), 1):
            print(f"\n{i:2}. {name}")
            print(f"    ON : {data['ON']}")
            print(f"    OFF: {data['OFF']}")
            if 'captured_at' in data:
                print(f"    캡처시간: {data['captured_at']}")
    
    def quick_capture_mode(self, device_type):
        """Quick capture for multiple devices"""
        if device_type == 'light':
            devices = [
                ('거실조명', '거실 조명'),
                ('방1조명', '방1 조명'),
                ('방2조명', '방2 조명'),
                ('방3조명', '방3 조명'),
                ('주방조명', '주방 조명')
            ]
        elif device_type == 'thermo':
            devices = [
                ('거실난방', '거실 난방'),
                ('방1난방', '방1 난방'),
                ('방2난방', '방2 난방'),
                ('방3난방', '방3 난방')
            ]
        else:
            return
        
        print(f"\n🚀 빠른 캡처 모드: {device_type}")
        print("각 장치를 순서대로 캡처합니다.\n")
        
        for device_id, device_desc in devices:
            if device_id in self.captured_devices:
                skip = input(f"\n'{device_id}'는 이미 캡처됨. 건너뛰시겠습니까? (y/n): ").strip().lower()
                if skip == 'y':
                    continue
            
            print(f"\n다음 장치: {device_desc}")
            ready = input("준비되면 Enter, 건너뛰려면 's' 입력: ").strip().lower()
            if ready == 's':
                continue
            
            success = self.capture_on_off_pair(device_id)
            if not success:
                stop = input("\n계속하시겠습니까? (y/n): ").strip().lower()
                if stop != 'y':
                    break
    
    def run(self):
        """Main interactive loop"""
        print("\n🏠 코콤 월패드 ON/OFF 패킷 캡처 도구")
        print("="*70)
        
        self.load_devices()
        
        if not self.connect():
            return
        
        while True:
            print("\n" + "-"*70)
            print("메뉴:")
            print("1. 장치 캡처 (ON/OFF 쌍)")
            print("2. 빠른 캡처 - 조명 전체")
            print("3. 빠른 캡처 - 난방 전체")
            print("4. 캡처된 장치 보기")
            print("5. 장치 삭제")
            print("6. 테스트 모드")
            print("0. 종료")
            print("-"*70)
            
            choice = input("\n선택: ").strip()
            
            if choice == '1':
                print("\n장치 이름을 입력하세요. (ON/OFF는 자동으로 관리됩니다)")
                print("예: 거실조명, 방1조명, 거실난방, 엘리베이터")
                device_name = input("\n장치 이름: ").strip()
                
                # Remove ON/OFF if user accidentally added it
                device_name = device_name.replace('ON', '').replace('OFF', '').replace('on', '').replace('off', '').strip()
                
                if device_name:
                    if device_name in self.captured_devices:
                        overwrite = input(f"'{device_name}' 덮어쓰시겠습니까? (y/n): ").strip().lower()
                        if overwrite != 'y':
                            continue
                    
                    self.capture_on_off_pair(device_name)
            
            elif choice == '2':
                self.quick_capture_mode('light')
            
            elif choice == '3':
                self.quick_capture_mode('thermo')
            
            elif choice == '4':
                self.show_devices()
            
            elif choice == '5':
                self.show_devices()
                if self.captured_devices:
                    del_name = input("\n삭제할 장치 이름: ").strip()
                    if del_name in self.captured_devices:
                        del self.captured_devices[del_name]
                        self.save_devices()
                        print(f"✅ '{del_name}' 삭제됨")
            
            elif choice == '6':
                print("\n🧪 테스트 모드")
                print("캡처된 패킷을 실제로 전송하여 테스트합니다.")
                self.show_devices()
                if self.captured_devices:
                    test_name = input("\n테스트할 장치: ").strip()
                    if test_name in self.captured_devices:
                        test_cmd = input("명령 (ON/OFF): ").strip().upper()
                        if test_cmd in ['ON', 'OFF']:
                            packet = self.captured_devices[test_name][test_cmd]
                            print(f"전송: {packet}")
                            # Convert packet string to bytes and send
                            hex_bytes = bytes.fromhex(packet.replace(' ', ''))
                            self.sock.send(hex_bytes)
                            print("✅ 전송 완료")
            
            elif choice == '0':
                break
        
        print(f"\n📊 총 {len(self.captured_devices)}개 장치 캡처 완료")
        if self.captured_devices:
            print(f"📁 저장 위치: {self.capture_file}")
        
        if self.sock:
            self.sock.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 capture_tool.py <IP> <PORT>")
        print("Example: python3 capture_tool.py 192.168.0.222 8899")
        sys.exit(1)
    
    capture = PairedPacketCapture(sys.argv[1], int(sys.argv[2]))
    capture.run()

if __name__ == "__main__":
    main()