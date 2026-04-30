#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kocom Light Interactive Test Tool
JSON 설정 기반 조명 테스트 대화형 프로그램
"""

import json
import socket
import time
from pathlib import Path


class LightTester:
    def __init__(self):
        self.load_config()
        self.conn = None
        self.server = None
        self.port = None

    def load_config(self):
        """Load JSON configuration files"""
        script_dir = Path(__file__).parent

        # Load protocol configuration
        with open(script_dir / 'protocol.json', 'r', encoding='utf-8') as f:
            self.protocol_config = json.load(f)

        # Load packet configuration
        with open(script_dir / 'packets.json', 'r', encoding='utf-8') as f:
            self.packet_config = json.load(f)

        # Extract configurations (code → name)
        self.device_codes = self.packet_config['devices']
        self.cmd_codes = self.packet_config['commands']
        self.rooms = self.packet_config['rooms']
        self.room_aliases = self.packet_config['room_aliases']

        # Create reverse mappings (name → code)
        self.device_names = {v: k for k, v in self.device_codes.items()}
        self.cmd_names = {v: k for k, v in self.cmd_codes.items()}
        self.room_names = {v: k for k, v in self.rooms.items()}

        self.header = self.protocol_config['packet_structure']['header']
        self.trailer = self.protocol_config['packet_structure']['trailer']

        print("[CONFIG] Loaded configuration from JSON files")
        print(f"  - Devices: {list(self.device_codes.values())}")
        print(f"  - Rooms: {list(self.rooms.values())}")

    def connect(self, server, port):
        """Connect to RS485 gateway"""
        try:
            self.server = server
            self.port = port
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.settimeout(5)
            self.conn.connect((server, port))
            print(f"[CONNECT] Connected to {server}:{port}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from RS485 gateway"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("[DISCONNECT] Disconnected from gateway")

    def chksum(self, data_h):
        """Calculate checksum"""
        sum_buf = sum(bytearray.fromhex(data_h))
        return '{0:02x}'.format(sum_buf % 256)

    def send_packet(self, dest, src, cmd, value):
        """Send RS485 packet"""
        type_h = '30bc'  # send packet type
        seq_h = 'c'  # first sequence
        monitor_h = '00'  # wallpad

        data_h = type_h + seq_h + monitor_h + dest + src + cmd + value
        chksum_h = self.chksum(data_h)
        packet_h = self.header + data_h + chksum_h + self.trailer

        print(f"[SEND] {packet_h}")
        try:
            self.conn.send(bytearray.fromhex(packet_h))
            return True
        except Exception as e:
            print(f"[ERROR] Send failed: {e}")
            return False

    def send_light_command(self, room_code, light_num, on_off):
        """Send light on/off command"""
        light_code = self.device_names['light']  # name → code lookup
        light_controller = '5400'  # 덕계역금강펜트리움 전용
        cmd_code = self.cmd_names['state']  # name → code lookup

        dest = light_code + room_code
        src = light_controller
        cmd = cmd_code

        # Build value - 8 bytes for 4 lights
        # Each light: ff=ON, 00=OFF
        value = '0000000000000000'  # Start with all off

        if on_off.lower() == 'on':
            onoff_hex = 'ff'
        else:
            onoff_hex = '00'

        # Set the specific light position
        pos = (light_num - 1) * 2
        value = value[:pos] + onoff_hex + value[pos+2:]

        print(f"\n[LIGHT] Room: {room_code}, Light: {light_num}, Command: {on_off.upper()}")
        print(f"  Dest: {dest}, Src: {src}, Cmd: {cmd}, Value: {value}")

        return self.send_packet(dest, src, cmd, value)

    def send_batch_off(self):
        """Send batch-off packet"""
        batch_config = self.packet_config['special_packets']['batch_off']
        packet_hex = batch_config['hex']

        print(f"\n[BATCH_OFF] Sending batch-off packet")
        print(f"  Packet: {packet_hex}")

        try:
            self.conn.send(bytearray.fromhex(packet_hex))
            return True
        except Exception as e:
            print(f"[ERROR] Batch-off failed: {e}")
            return False

    def send_batch_off_continuous(self, duration=5, interval=0.3):
        """Send batch-off continuously"""
        batch_config = self.packet_config['special_packets']['batch_off']
        packet_hex = batch_config['hex']

        print(f"\n[BATCH_OFF_CONTINUOUS] Duration: {duration}s, Interval: {interval}s")

        end_time = time.time() + duration
        count = 0
        try:
            while time.time() < end_time:
                self.conn.send(bytearray.fromhex(packet_hex))
                count += 1
                if count % 5 == 0:
                    print(f"  Progress: {count} packets sent")
                time.sleep(interval)
            print(f"[BATCH_OFF_CONTINUOUS] Complete - {count} packets sent")
            return True
        except Exception as e:
            print(f"[ERROR] Batch-off continuous failed: {e}")
            return False

    def show_menu(self):
        """Show interactive menu"""
        print("\n" + "="*60)
        print("Kocom Light Interactive Test Tool")
        print("="*60)
        print("\n[Main Menu]")
        print("  1. 조명 켜기 (Turn ON light)")
        print("  2. 조명 끄기 (Turn OFF light)")
        print("  3. 일괄소등 해제 - 단발 (Batch OFF - Single)")
        print("  4. 일괄소등 해제 - 연속 (Batch OFF - Continuous)")
        print("  5. 재연결 (Reconnect)")
        print("  0. 종료 (Exit)")
        print("\n" + "="*60)

    def show_rooms(self):
        """Show room selection menu"""
        print("\n[방 선택 / Select Room]")
        room_list = []

        # Room name mapping for better Korean display
        korean_map = {
            'livingroom': '거실',
            'master': '안방',
            'office': '작업실',
            'guest': '손님방',
            'kitchen': '주방'
        }

        for i, (code, name) in enumerate(self.rooms.items(), 1):
            korean_name = korean_map.get(name, name)
            room_list.append((code, name, korean_name))
            print(f"  {i}. {korean_name} ({name})")
        return room_list

    def get_room_choice(self):
        """Get room selection from user"""
        room_list = self.show_rooms()
        while True:
            try:
                choice = input("\n방 번호를 선택하세요 (1-{}): ".format(len(room_list))).strip()
                if not choice:
                    return None
                choice = int(choice)
                if 1 <= choice <= len(room_list):
                    return room_list[choice - 1][0]  # Return room code
                else:
                    print(f"[ERROR] 1-{len(room_list)} 사이의 숫자를 입력하세요")
            except ValueError:
                print("[ERROR] 숫자를 입력하세요")
            except KeyboardInterrupt:
                return None

    def get_light_number(self):
        """Get light number from user"""
        print("\n[조명 선택 / Select Light]")
        print("  1. 조명 1")
        print("  2. 조명 2")
        print("  3. 조명 3")
        print("  4. 조명 4")
        while True:
            try:
                choice = input("\n조명 번호를 선택하세요 (1-4): ").strip()
                if not choice:
                    return None
                choice = int(choice)
                if 1 <= choice <= 4:
                    return choice
                else:
                    print("[ERROR] 1-4 사이의 숫자를 입력하세요")
            except ValueError:
                print("[ERROR] 숫자를 입력하세요")
            except KeyboardInterrupt:
                return None

    def get_duration(self):
        """Get duration for continuous batch-off"""
        print("\n[지속 시간 설정 / Set Duration]")
        while True:
            try:
                duration = input("초 단위로 입력하세요 [기본값: 5초]: ").strip()
                if not duration:
                    return 5
                duration = int(duration)
                if duration > 0:
                    return duration
                else:
                    print("[ERROR] 양수를 입력하세요")
            except ValueError:
                print("[ERROR] 숫자를 입력하세요")
            except KeyboardInterrupt:
                return None

    def run(self):
        """Run interactive test"""
        print("\n" + "="*60)
        print("Kocom Light Interactive Test Tool")
        print("코콤 조명 테스트 도구")
        print("="*60)

        # Get connection info
        print("\n[연결 설정 / Connection Setup]")
        server = input("RS485 게이트웨이 IP [192.168.0.222]: ").strip() or "192.168.0.222"
        port_input = input("RS485 게이트웨이 포트 [8899]: ").strip() or "8899"
        port = int(port_input)

        if not self.connect(server, port):
            return

        try:
            while True:
                self.show_menu()

                choice = input("\n메뉴를 선택하세요 (0-5): ").strip()

                if not choice:
                    continue

                try:
                    choice = int(choice)
                except ValueError:
                    print("[ERROR] 숫자를 입력하세요")
                    continue

                # 0. Exit
                if choice == 0:
                    print("\n[EXIT] 프로그램을 종료합니다...")
                    break

                # 1. Turn ON light
                elif choice == 1:
                    room_code = self.get_room_choice()
                    if room_code is None:
                        continue

                    light_num = self.get_light_number()
                    if light_num is None:
                        continue

                    if self.send_light_command(room_code, light_num, 'on'):
                        room_name = self.rooms[room_code]
                        korean_names = [k for k, v in self.room_aliases.items() if v == room_code and len(k) > 2]
                        korean_name = korean_names[0] if korean_names else room_name
                        print(f"\n[성공] {korean_name} 조명 {light_num}번을 켰습니다")
                        print(f"[OK] Light {light_num} in {room_name} turned ON")

                # 2. Turn OFF light
                elif choice == 2:
                    room_code = self.get_room_choice()
                    if room_code is None:
                        continue

                    light_num = self.get_light_number()
                    if light_num is None:
                        continue

                    if self.send_light_command(room_code, light_num, 'off'):
                        room_name = self.rooms[room_code]
                        korean_names = [k for k, v in self.room_aliases.items() if v == room_code and len(k) > 2]
                        korean_name = korean_names[0] if korean_names else room_name
                        print(f"\n[성공] {korean_name} 조명 {light_num}번을 껐습니다")
                        print(f"[OK] Light {light_num} in {room_name} turned OFF")

                # 3. Batch OFF (single)
                elif choice == 3:
                    print("\n[일괄소등 해제 - 단발]")
                    confirm = input("일괄소등 해제 패킷을 전송하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y' or confirm == 'yes':
                        if self.send_batch_off():
                            print("\n[성공] 일괄소등 해제 패킷을 전송했습니다")
                            print("[OK] Batch-off packet sent")

                # 4. Batch OFF (continuous)
                elif choice == 4:
                    duration = self.get_duration()
                    if duration is None:
                        continue

                    print(f"\n[일괄소등 해제 - 연속] {duration}초간 전송합니다...")
                    if self.send_batch_off_continuous(duration=duration):
                        print(f"\n[성공] {duration}초간 일괄소등 해제 패킷을 전송했습니다")
                        print(f"[OK] Batch-off continuous for {duration}s complete")

                # 5. Reconnect
                elif choice == 5:
                    print("\n[재연결]")
                    self.disconnect()
                    if self.connect(self.server, self.port):
                        print("\n[성공] 재연결되었습니다")
                        print("[OK] Reconnected successfully")

                else:
                    print(f"[ERROR] 잘못된 선택입니다. 0-5 사이의 숫자를 입력하세요")

        except KeyboardInterrupt:
            print("\n\n[EXIT] 사용자에 의해 중단되었습니다")
            print("[EXIT] Interrupted by user")
        finally:
            self.disconnect()


if __name__ == '__main__':
    tester = LightTester()
    tester.run()
