#!/usr/bin/env python3
"""
Interactive Kocom Wallpad Packet Capture Tool
Captures and saves actual wallpad packets for each function
"""

import socket
import json
import time
import sys
import os
from datetime import datetime

class PacketCapture:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.captured_packets = {}
        self.sock = None
        self.buffer = ""
        self.last_packet = None
        self.capture_file = "captured_packets.json"
        
    def connect(self):
        """Connect to EW11"""
        print(f"\n📡 Connecting to {self.server_ip}:{self.server_port}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)  # 10 second timeout
            self.sock.connect((self.server_ip, self.server_port))
            print("✅ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def capture_single_packet(self, timeout=5):
        """Capture a single packet with timeout"""
        start_time = time.time()
        self.buffer = ""
        
        while time.time() - start_time < timeout:
            try:
                self.sock.settimeout(0.5)
                data = self.sock.recv(1024)
                if data:
                    hex_data = data.hex()
                    self.buffer += hex_data
                    
                    # Look for complete packet
                    if 'aa55' in self.buffer and '0d0d' in self.buffer:
                        start_pos = self.buffer.index('aa55')
                        end_pos = self.buffer.index('0d0d', start_pos) + 4
                        
                        if end_pos > start_pos:
                            packet = self.buffer[start_pos:end_pos]
                            self.buffer = self.buffer[end_pos:]
                            
                            # Format packet
                            formatted = ' '.join([packet[i:i+2] for i in range(0, len(packet), 2)])
                            return formatted.upper()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        return None
    
    def capture_function(self, function_name):
        """Capture packets for a specific function"""
        print("\n" + "="*60)
        print(f"📌 캡처할 기능: {function_name}")
        print("="*60)
        print("\n지금부터 월패드에서 해당 동작을 2번 수행해주세요.")
        print("각 동작 사이에 2-3초 간격을 두세요.\n")
        
        captured = []
        
        # First capture
        input("🔴 첫 번째 동작 준비되면 Enter를 누르고, 5초 내에 버튼을 누르세요...")
        print("⏱️  캡처 중... (5초)")
        packet1 = self.capture_single_packet(5)
        
        if packet1:
            print(f"✅ 패킷 1 캡처됨: {packet1}")
            captured.append(packet1)
        else:
            print("❌ 패킷을 캡처하지 못했습니다.")
        
        time.sleep(2)
        
        # Second capture (verification)
        input("\n🔴 두 번째 동작 준비되면 Enter를 누르고, 5초 내에 같은 버튼을 다시 누르세요...")
        print("⏱️  캡처 중... (5초)")
        packet2 = self.capture_single_packet(5)
        
        if packet2:
            print(f"✅ 패킷 2 캡처됨: {packet2}")
            captured.append(packet2)
        else:
            print("❌ 패킷을 캡처하지 못했습니다.")
        
        # Verify packets
        if len(captured) == 2:
            if captured[0] == captured[1]:
                print(f"\n✅ 검증 완료! 동일한 패킷이 2번 캡처되었습니다.")
                self.captured_packets[function_name] = captured[0]
                self.save_packets()
                return True
            else:
                print(f"\n⚠️ 경고: 두 패킷이 다릅니다!")
                print(f"패킷 1: {captured[0]}")
                print(f"패킷 2: {captured[1]}")
                
                choice = input("\n어느 패킷을 사용하시겠습니까? (1/2/다시/취소): ").strip()
                if choice == '1':
                    self.captured_packets[function_name] = captured[0]
                    self.save_packets()
                    return True
                elif choice == '2':
                    self.captured_packets[function_name] = captured[1]
                    self.save_packets()
                    return True
                elif choice == '다시':
                    return self.capture_function(function_name)
                else:
                    return False
        else:
            print("\n❌ 패킷 캡처 실패. 다시 시도해주세요.")
            retry = input("다시 시도하시겠습니까? (y/n): ").strip().lower()
            if retry == 'y':
                return self.capture_function(function_name)
            return False
    
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
            print(f"{i}. {name}: {packet}")
    
    def interactive_capture(self):
        """Main interactive capture loop"""
        print("\n🎯 코콤 월패드 패킷 캡처 시스템")
        print("="*60)
        
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
            print("4. 모든 패킷 삭제")
            print("5. 종료")
            print("-"*60)
            
            choice = input("\n선택 (1-5): ").strip()
            
            if choice == '1':
                print("\n캡처할 기능 이름을 입력하세요.")
                print("예시: 거실조명ON, 거실조명OFF, 방1조명ON, 거실온도23도, 엘리베이터호출")
                function_name = input("\n기능 이름: ").strip()
                
                if function_name:
                    if function_name in self.captured_packets:
                        overwrite = input(f"'{function_name}'은 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ").strip().lower()
                        if overwrite != 'y':
                            continue
                    
                    self.capture_function(function_name)
                    
                    cont = input("\n계속 캡처하시겠습니까? (y/n): ").strip().lower()
                    if cont != 'y':
                        break
            
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
                    else:
                        print(f"❌ '{del_name}'을 찾을 수 없습니다.")
            
            elif choice == '4':
                confirm = input("정말 모든 패킷을 삭제하시겠습니까? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    self.captured_packets = {}
                    self.save_packets()
                    print("✅ 모든 패킷이 삭제되었습니다.")
            
            elif choice == '5':
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
        print("Usage: python3 interactive_capture.py <IP_ADDRESS> <PORT>")
        print("Example: python3 interactive_capture.py 192.168.0.222 8899")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    capture = PacketCapture(server_ip, server_port)
    capture.interactive_capture()

if __name__ == "__main__":
    main()