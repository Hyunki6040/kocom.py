#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kocom Wallpad Interactive Test Tool
JSON 설정 기반 월패드 전체 기능 테스트 대화형 프로그램
- 조명, 난방, 환풍기, 가스, 엘리베이터, 일괄소등 제어
"""

import json
import socket
import time
from pathlib import Path


class WallpadTester:
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
        self.room_lights = self.packet_config.get('room_lights', {})  # 방별 조명 개수

        # Protocol configurations
        self.packet_types = self.protocol_config['packet_types']
        self.sequence_codes = self.protocol_config['sequence_codes']

        # Create reverse mappings (name → code)
        self.device_names = {v: k for k, v in self.device_codes.items()}
        self.cmd_names = {v: k for k, v in self.cmd_codes.items()}
        self.room_names = {v: k for k, v in self.rooms.items()}
        self.type_codes = {v: k for k, v in self.packet_types.items()}

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
        type_h = self.type_codes['send']  # '30b' (3 chars, not '30bc')
        seq_h = 'c'  # first sequence (1 char)
        monitor_h = '00'  # wallpad (2 chars)

        # Total: 3 + 1 + 2 + 4 + 4 + 2 + 16 = 32 chars (even number for hex)
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

    def send_thermostat_command(self, room_code, command, value=None):
        """Send thermostat command"""
        thermo_code = self.device_names['thermo']
        wallpad = self.device_names['wallpad'] + '00'

        dest = thermo_code + room_code
        src = wallpad

        if command == 'heat_on':
            # Heat mode ON with temperature
            temp_hex = '{0:02x}'.format(int(value)) if value else '16'  # Default 22°C
            cmd = self.cmd_names['state']
            packet_value = '11' + temp_hex + '000000000000'  # 11 = heat mode on
        elif command == 'heat_off':
            # Heat mode OFF
            cmd = self.cmd_names['state']
            packet_value = '0000000000000000'
        else:
            return False

        print(f"\n[THERMO] Room: {room_code}, Command: {command}, Value: {packet_value}")
        return self.send_packet(dest, src, cmd, packet_value)

    def send_elevator_call(self):
        """Call elevator"""
        elevator_code = self.device_names['elevator']
        wallpad = self.device_names['wallpad'] + '00'

        dest = elevator_code + '00'
        src = wallpad
        cmd = self.cmd_names['on']
        value = '0000000000000000'

        print(f"\n[ELEVATOR] Calling elevator")
        return self.send_packet(dest, src, cmd, value)

    def send_fan_command(self, preset):
        """Send fan command"""
        fan_code = self.device_names['fan']
        wallpad = self.device_names['wallpad'] + '00'

        dest = fan_code + '00'
        src = wallpad
        cmd = self.cmd_names['state']

        # Fan presets from packets.json parsing.fan.presets
        preset_map = {
            'off': '0000000000000000',
            'low': '4000000000000000',
            'medium': '8000000000000000',
            'high': 'c000000000000000'
        }

        value = preset_map.get(preset.lower(), '0000000000000000')

        print(f"\n[FAN] Preset: {preset}, Value: {value}")
        return self.send_packet(dest, src, cmd, value)

    def send_gas_off(self):
        """Send gas OFF command"""
        gas_code = self.device_names['gas']
        wallpad = self.device_names['wallpad'] + '00'

        dest = gas_code + '00'
        src = wallpad
        cmd = self.cmd_names['off']
        value = '0000000000000000'

        print(f"\n[GAS] Sending gas OFF command")
        return self.send_packet(dest, src, cmd, value)

    def send_batch_on(self):
        """Send batch ON (일괄소등 활성화) packet"""
        batch_config = self.packet_config.get('special_packets', {}).get('batch_on')
        if not batch_config:
            # Fallback: construct batch ON packet
            packet_hex = 'aa55309c000eff01006500000000000000003f0d0d'
        else:
            packet_hex = batch_config['hex']

        print(f"\n[BATCH_ON] Sending batch-on packet")
        print(f"  Packet: {packet_hex}")

        try:
            self.conn.send(bytearray.fromhex(packet_hex))
            return True
        except Exception as e:
            print(f"[ERROR] Batch-on failed: {e}")
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
        print("Kocom Wallpad Interactive Test Tool")
        print("코콤 월패드 테스트 도구")
        print("="*60)
        print("\n[Main Menu]")
        print("  1. 조명 제어 (Light Control)")
        print("  2. 난방 제어 (Thermostat Control)")
        print("  3. 엘리베이터 호출 (Call Elevator)")
        print("  4. 환풍기 제어 (Fan Control)")
        print("  5. 가스 차단 (Gas Cutoff)")
        print("  6. 일괄소등 제어 (Batch Control)")
        print("  7. 재연결 (Reconnect)")
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

    def get_light_number(self, room_code):
        """Get light number from user based on room"""
        max_lights = self.room_lights.get(room_code, 4)  # 기본값 4

        # 조명이 없는 방
        if max_lights == 0:
            print("\n[알림] 이 방에는 조명이 없습니다.")
            print("[INFO] This room has no lights.")
            input("\n아무 키나 눌러 계속...")
            return None

        print("\n[조명 선택 / Select Light]")
        for i in range(1, max_lights + 1):
            print(f"  {i}. 조명 {i}")

        while True:
            try:
                choice = input(f"\n조명 번호를 선택하세요 (1-{max_lights}): ").strip()
                if not choice:
                    return None
                choice = int(choice)
                if 1 <= choice <= max_lights:
                    return choice
                else:
                    print(f"[ERROR] 1-{max_lights} 사이의 숫자를 입력하세요")
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
        print("Kocom Wallpad Interactive Test Tool")
        print("코콤 월패드 테스트 도구")
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

                choice = input("\n메뉴를 선택하세요 (0-7): ").strip()

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

                # 1. Light Control
                elif choice == 1:
                    print("\n[조명 제어 / Light Control]")
                    print("  1. 켜기 (ON)")
                    print("  2. 끄기 (OFF)")
                    sub_choice = input("선택: ").strip()

                    if sub_choice not in ['1', '2']:
                        continue

                    room_code = self.get_room_choice()
                    if room_code is None:
                        continue

                    light_num = self.get_light_number(room_code)
                    if light_num is None:
                        continue

                    on_off = 'on' if sub_choice == '1' else 'off'
                    if self.send_light_command(room_code, light_num, on_off):
                        room_name = self.rooms[room_code]
                        korean_names = [k for k, v in self.room_aliases.items() if v == room_code and len(k) > 2]
                        korean_name = korean_names[0] if korean_names else room_name
                        action_kr = "켰습니다" if on_off == 'on' else "껐습니다"
                        action_en = "ON" if on_off == 'on' else "OFF"
                        print(f"\n[성공] {korean_name} 조명 {light_num}번을 {action_kr}")
                        print(f"[OK] Light {light_num} in {room_name} turned {action_en}")

                # 2. Thermostat Control
                elif choice == 2:
                    print("\n[난방 제어 / Thermostat Control]")
                    room_code = self.get_room_choice()
                    if room_code is None:
                        continue

                    print("\n[제어 선택]")
                    print("  1. 난방 켜기 (Heat ON)")
                    print("  2. 난방 끄기 (Heat OFF)")
                    sub_choice = input("선택: ").strip()

                    if sub_choice == '1':
                        # Heat ON - ask for temperature
                        temp_input = input("온도 설정 (5-30°C) [기본값: 22]: ").strip()
                        temp = int(temp_input) if temp_input else 22
                        if temp < 5 or temp > 30:
                            print("[ERROR] 온도는 5-30°C 사이여야 합니다")
                            continue

                        if self.send_thermostat_command(room_code, 'heat_on', temp):
                            room_name = self.rooms[room_code]
                            korean_names = [k for k, v in self.room_aliases.items() if v == room_code and len(k) > 2]
                            korean_name = korean_names[0] if korean_names else room_name
                            print(f"\n[성공] {korean_name} 난방을 {temp}°C로 설정했습니다")
                            print(f"[OK] {room_name} thermostat set to {temp}°C")

                    elif sub_choice == '2':
                        # Heat OFF
                        if self.send_thermostat_command(room_code, 'heat_off'):
                            room_name = self.rooms[room_code]
                            korean_names = [k for k, v in self.room_aliases.items() if v == room_code and len(k) > 2]
                            korean_name = korean_names[0] if korean_names else room_name
                            print(f"\n[성공] {korean_name} 난방을 껐습니다")
                            print(f"[OK] {room_name} thermostat turned OFF")

                # 3. Elevator Call
                elif choice == 3:
                    print("\n[엘리베이터 호출 / Call Elevator]")
                    confirm = input("엘리베이터를 호출하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y' or confirm == 'yes':
                        if self.send_elevator_call():
                            print("\n[성공] 엘리베이터 호출 신호를 전송했습니다")
                            print("[OK] Elevator call signal sent")

                # 4. Fan Control
                elif choice == 4:
                    print("\n[환풍기 제어 / Fan Control]")
                    print("  1. 끄기 (OFF)")
                    print("  2. 약 (Low)")
                    print("  3. 중 (Medium)")
                    print("  4. 강 (High)")
                    sub_choice = input("선택: ").strip()

                    preset_map = {'1': 'off', '2': 'low', '3': 'medium', '4': 'high'}
                    preset = preset_map.get(sub_choice)

                    if preset:
                        if self.send_fan_command(preset):
                            preset_kr = {'off': '끄기', 'low': '약', 'medium': '중', 'high': '강'}
                            print(f"\n[성공] 환풍기를 {preset_kr[preset]}로 설정했습니다")
                            print(f"[OK] Fan set to {preset.upper()}")

                # 5. Gas Cutoff
                elif choice == 5:
                    print("\n[가스 차단 / Gas Cutoff]")
                    confirm = input("가스를 차단하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y' or confirm == 'yes':
                        if self.send_gas_off():
                            print("\n[성공] 가스 차단 신호를 전송했습니다")
                            print("[OK] Gas cutoff signal sent")

                # 6. Batch Control
                elif choice == 6:
                    print("\n[일괄소등 제어 / Batch Control]")
                    print("  1. 일괄소등 활성화 (Batch ON - 모든 조명 끔)")
                    print("  2. 일괄소등 해제 (Batch OFF - 단발)")
                    print("  3. 일괄소등 해제 (Batch OFF - 연속)")
                    sub_choice = input("선택: ").strip()

                    if sub_choice == '1':
                        confirm = input("일괄소등을 활성화하시겠습니까? (y/n): ").strip().lower()
                        if confirm == 'y' or confirm == 'yes':
                            if self.send_batch_on():
                                print("\n[성공] 일괄소등 활성화 패킷을 전송했습니다")
                                print("[OK] Batch-on packet sent")

                    elif sub_choice == '2':
                        confirm = input("일괄소등 해제 패킷을 전송하시겠습니까? (y/n): ").strip().lower()
                        if confirm == 'y' or confirm == 'yes':
                            if self.send_batch_off():
                                print("\n[성공] 일괄소등 해제 패킷을 전송했습니다")
                                print("[OK] Batch-off packet sent")

                    elif sub_choice == '3':
                        duration = self.get_duration()
                        if duration is None:
                            continue
                        print(f"\n[일괄소등 해제 - 연속] {duration}초간 전송합니다...")
                        if self.send_batch_off_continuous(duration=duration):
                            print(f"\n[성공] {duration}초간 일괄소등 해제 패킷을 전송했습니다")
                            print(f"[OK] Batch-off continuous for {duration}s complete")

                # 7. Reconnect
                elif choice == 7:
                    print("\n[재연결]")
                    self.disconnect()
                    if self.connect(self.server, self.port):
                        print("\n[성공] 재연결되었습니다")
                        print("[OK] Reconnected successfully")

                else:
                    print("[ERROR] 잘못된 선택입니다. 0-7 사이의 숫자를 입력하세요")

        except KeyboardInterrupt:
            print("\n\n[EXIT] 사용자에 의해 중단되었습니다")
            print("[EXIT] Interrupted by user")
        finally:
            self.disconnect()


if __name__ == '__main__':
    tester = WallpadTester()
    tester.run()
