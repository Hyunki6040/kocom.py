#!/usr/bin/env python3
"""
Interactive Kocom Wallpad Packet Capture Tool v2
Captures baseline and action packets to find the difference
"""

import socket
import json
import time
import sys
import os
from datetime import datetime
from collections import Counter

class PacketCaptureV2:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.captured_packets = {}
        self.sock = None
        self.capture_file = "captured_packets.json"
        
    def connect(self):
        """Connect to EW11"""
        print(f"\n📡 Connecting to {self.server_ip}:{self.server_port}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.1)  # Short timeout for non-blocking
            self.sock.connect((self.server_ip, self.server_port))
            print("✅ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def capture_packets_for_duration(self, duration):
        """Capture all packets for a given duration"""
        packets = []
        buffer = ""
        start_time = time.time()
        
        print(f"⏱️  캡처 중... ({duration}초)")
        
        while time.time() - start_time < duration:
            try:
                data = self.sock.recv(4096)
                if data:
                    hex_data = data.hex()
                    buffer += hex_data
                    
                    # Extract all complete packets
                    while 'aa55' in buffer and '0d0d' in buffer:
                        try:
                            start_pos = buffer.index('aa55')
                            end_pos = buffer.index('0d0d', start_pos) + 4
                            
                            if end_pos > start_pos:
                                packet = buffer[start_pos:end_pos]
                                buffer = buffer[end_pos:]
                                
                                # Format packet
                                formatted = ' '.join([packet[i:i+2] for i in range(0, len(packet), 2)])
                                packets.append(formatted.upper())
                            else:
                                break
                        except ValueError:
                            break
            except socket.timeout:
                continue
            except Exception:
                continue
        
        return packets
    
    def analyze_packets(self, baseline, action):
        """Find packets that appear in action but not in baseline"""
        baseline_counter = Counter(baseline)
        action_counter = Counter(action)
        
        # Find new packets (in action but not in baseline)
        new_packets = []
        for packet, count in action_counter.items():
            if packet not in baseline_counter:
                new_packets.append(packet)
            elif count > baseline_counter[packet]:
                # Packet appears more times in action
                new_packets.append(packet)
        
        return new_packets
    
    def capture_function(self, function_name):
        """Capture packets for a specific function using baseline comparison"""
        print("\n" + "="*60)
        print(f"📌 캡처할 기능: {function_name}")
        print("="*60)
        
        # Step 1: Capture baseline (no action)
        print("\n[1단계] 기준선 캡처")
        print("월패드를 조작하지 마시고 기다려주세요.")
        input("준비되면 Enter를 누르세요...")
        baseline_packets = self.capture_packets_for_duration(5)
        print(f"✅ 기준선: {len(baseline_packets)}개 패킷 캡처")
        
        # Show baseline pattern
        baseline_unique = list(set(baseline_packets))
        print(f"   유니크 패킷: {len(baseline_unique)}개")
        
        time.sleep(2)
        
        # Step 2: Capture with action
        print("\n[2단계] 동작 캡처")
        print(f"이제 '{function_name}' 동작을 수행해주세요.")
        print("캡처가 시작되면 5초 내에 버튼을 1번만 누르세요.")
        input("준비되면 Enter를 누르세요...")
        action_packets = self.capture_packets_for_duration(5)
        print(f"✅ 동작시: {len(action_packets)}개 패킷 캡처")
        
        # Find difference
        new_packets = self.analyze_packets(baseline_packets, action_packets)
        
        if new_packets:
            print(f"\n🎯 새로운 패킷 {len(new_packets)}개 발견:")
            for i, packet in enumerate(new_packets, 1):
                print(f"  {i}. {packet}")
                # Parse packet info
                self.show_packet_info(packet)
            
            # Step 3: Verify with second capture
            print("\n[3단계] 검증")
            print("같은 동작을 한 번 더 수행하여 검증합니다.")
            input("준비되면 Enter를 누르세요...")
            
            # Capture baseline again
            print("먼저 다시 기준선 캡처 (아무것도 누르지 마세요)...")
            baseline2 = self.capture_packets_for_duration(3)
            
            time.sleep(2)
            
            print("이제 같은 버튼을 다시 누르세요.")
            input("준비되면 Enter를 누르세요...")
            verify_packets = self.capture_packets_for_duration(5)
            
            # Find new packets in verification
            verify_new = self.analyze_packets(baseline2, verify_packets)
            
            # Find common packets
            common_packets = [p for p in new_packets if p in verify_new]
            
            if common_packets:
                print(f"\n✅ 검증 완료! 공통 패킷 {len(common_packets)}개:")
                for i, packet in enumerate(common_packets, 1):
                    print(f"  {i}. {packet}")
                
                if len(common_packets) == 1:
                    # Single packet - save it
                    self.captured_packets[function_name] = common_packets[0]
                    print(f"\n✅ '{function_name}' 패킷 저장됨")
                else:
                    # Multiple packets - let user choose
                    print("\n여러 개의 패킷이 발견되었습니다.")
                    choice = input(f"어느 패킷을 사용하시겠습니까? (1-{len(common_packets)}): ").strip()
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(common_packets):
                            self.captured_packets[function_name] = common_packets[idx]
                            print(f"\n✅ '{function_name}' 패킷 저장됨")
                    except:
                        print("❌ 잘못된 선택")
                
                self.save_packets()
                return True
            else:
                print("\n⚠️ 검증 실패: 일치하는 패킷이 없습니다.")
                print("새 패킷 (첫 번째):", new_packets[:3] if len(new_packets) > 3 else new_packets)
                print("새 패킷 (두 번째):", verify_new[:3] if len(verify_new) > 3 else verify_new)
        else:
            print("\n❌ 새로운 패킷이 감지되지 않았습니다.")
            print("버튼을 더 세게 누르거나, 다른 버튼을 시도해보세요.")
        
        retry = input("\n다시 시도하시겠습니까? (y/n): ").strip().lower()
        if retry == 'y':
            return self.capture_function(function_name)
        return False
    
    def show_packet_info(self, packet):
        """Show packet structure information"""
        parts = packet.split()
        if len(parts) >= 10 and parts[0] == 'AA' and parts[1] == '55':
            device_codes = {
                '00 0E': '조명',
                '00 36': '온도조절기',
                '00 2C': '가스',
                '00 44': '엘리베이터',
                '00 48': '환기팬'
            }
            
            device = ' '.join(parts[4:6])
            device_name = device_codes.get(device, f"Unknown({device})")
            print(f"      → 장치: {device_name}, Type: {parts[2]} {parts[3]}")
    
    def save_packets(self):
        """Save captured packets to file"""
        with open(self.capture_file, 'w') as f:
            json.dump(self.captured_packets, f, indent=2, ensure_ascii=False)
        print(f"💾 패킷이 {self.capture_file}에 저장되었습니다.")
    
    def load_packets(self):
        """Load previously captured packets"""
        if os.path.exists(self.capture_file):
            with open(self.capture_file, 'r') as f:
                self.captured_packets = json.load(f)
            print(f"📂 기존 패킷 {len(self.captured_packets)}개를 불러왔습니다.")
    
    def show_captured(self):
        """Show all captured packets"""
        if not self.captured_packets:
            print("\n캡처된 패킷이 없습니다.")
            return
        
        print("\n" + "="*60)
        print("📋 캡처된 패킷 목록")
        print("="*60)
        for i, (name, packet) in enumerate(self.captured_packets.items(), 1):
            print(f"{i:2}. {name:20} : {packet}")
    
    def interactive_capture(self):
        """Main interactive capture loop"""
        print("\n🎯 코콤 월패드 패킷 캡처 시스템 v2")
        print("="*60)
        print("기준선 비교 방식으로 정확한 패킷을 캡처합니다.")
        
        # Load existing packets
        self.load_packets()
        
        # Connect to EW11
        if not self.connect():
            return
        
        while True:
            print("\n" + "-"*60)
            print("메뉴:")
            print("1. 새 기능 캡처")
            print("2. 캡처된 패킷 보기")
            print("3. 캡처된 패킷 삭제")
            print("4. 빠른 캡처 모드 (조명 전체)")
            print("5. 빠른 캡처 모드 (온도조절기)")
            print("6. 종료 및 저장")
            print("-"*60)
            
            choice = input("\n선택 (1-6): ").strip()
            
            if choice == '1':
                print("\n캡처할 기능 이름을 입력하세요.")
                print("예시: 거실조명ON, 거실조명OFF, 방1조명ON, 거실온도UP")
                function_name = input("\n기능 이름: ").strip()
                
                if function_name:
                    if function_name in self.captured_packets:
                        overwrite = input(f"'{function_name}'은 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ").strip().lower()
                        if overwrite != 'y':
                            continue
                    
                    self.capture_function(function_name)
            
            elif choice == '2':
                self.show_captured()
            
            elif choice == '3':
                self.show_captured()
                if self.captured_packets:
                    del_name = input("\n삭제할 기능 이름: ").strip()
                    if del_name in self.captured_packets:
                        del self.captured_packets[del_name]
                        self.save_packets()
                        print(f"✅ '{del_name}' 삭제됨")
            
            elif choice == '4':
                # Quick capture for lights
                rooms = ['거실', '방1', '방2', '방3', '주방']
                for room in rooms:
                    for state in ['ON', 'OFF']:
                        name = f"{room}조명{state}"
                        if name not in self.captured_packets:
                            print(f"\n다음 캡처: {name}")
                            cont = input("계속하시겠습니까? (y/n): ").strip().lower()
                            if cont == 'y':
                                self.capture_function(name)
                            else:
                                break
            
            elif choice == '5':
                # Quick capture for thermostats
                rooms = ['거실', '방1', '방2', '방3']
                actions = ['온도UP', '온도DOWN', '난방ON', '난방OFF']
                for room in rooms:
                    for action in actions:
                        name = f"{room}{action}"
                        if name not in self.captured_packets:
                            print(f"\n다음 캡처: {name}")
                            cont = input("계속하시겠습니까? (y/n): ").strip().lower()
                            if cont == 'y':
                                self.capture_function(name)
                            else:
                                break
            
            elif choice == '6':
                print("\n캡처를 종료합니다.")
                self.show_captured()
                
                if self.captured_packets:
                    print(f"\n✅ 총 {len(self.captured_packets)}개의 패킷이 캡처되었습니다.")
                    print(f"📁 패킷은 {self.capture_file}에 저장되었습니다.")
                break
        
        if self.sock:
            self.sock.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 interactive_capture_v2.py <IP_ADDRESS> <PORT>")
        print("Example: python3 interactive_capture_v2.py 192.168.0.222 8899")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    capture = PacketCaptureV2(server_ip, server_port)
    capture.interactive_capture()

if __name__ == "__main__":
    main()