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

        # Extract configurations
        self.device_codes = self.packet_config['devices']
        self.cmd_codes = self.packet_config['commands']
        self.rooms = self.packet_config['rooms']
        self.room_aliases = self.packet_config['room_aliases']
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
        light_code = self.device_codes['light']
        light_controller = '5400'  # 덕계역금강펜트리움 전용
        cmd_code = self.cmd_codes['state']

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
        print("\n[Available Rooms]")
        for code, name in self.rooms.items():
            korean_name = [k for k, v in self.room_aliases.items() if v == code and len(k) > 2][0]
            print(f"  {code} - {name} ({korean_name})")

        print("\n[Commands]")
        print("  1. Turn ON light:  on <room_code> <light_num>")
        print("  2. Turn OFF light: off <room_code> <light_num>")
        print("  3. Batch OFF (single): batch_off")
        print("  4. Batch OFF (continuous): batch_cont <duration>")
        print("  5. Reconnect: reconnect")
        print("  6. Show menu: menu")
        print("  7. Exit: exit")
        print("\nExamples:")
        print("  on 00 1      - Turn ON livingroom light 1")
        print("  off 01 2     - Turn OFF master bedroom light 2")
        print("  batch_cont 5 - Send batch-off continuously for 5 seconds")

    def run(self):
        """Run interactive test"""
        print("\nKocom Light Interactive Test Tool")
        print("="*60)

        # Get connection info
        server = input("Enter RS485 gateway IP [192.168.0.222]: ").strip() or "192.168.0.222"
        port = input("Enter RS485 gateway port [8899]: ").strip() or "8899"
        port = int(port)

        if not self.connect(server, port):
            return

        self.show_menu()

        try:
            while True:
                cmd_input = input("\n>>> ").strip()

                if not cmd_input:
                    continue

                parts = cmd_input.split()
                cmd = parts[0].lower()

                if cmd == 'exit' or cmd == 'quit':
                    break

                elif cmd == 'menu' or cmd == 'help':
                    self.show_menu()

                elif cmd == 'reconnect':
                    self.disconnect()
                    if self.connect(self.server, self.port):
                        print("[OK] Reconnected successfully")

                elif cmd == 'on' or cmd == 'off':
                    if len(parts) < 3:
                        print("[ERROR] Usage: on/off <room_code> <light_num>")
                        continue

                    room_code = parts[1]
                    try:
                        light_num = int(parts[2])
                    except ValueError:
                        print("[ERROR] Light number must be integer")
                        continue

                    if room_code not in self.rooms:
                        print(f"[ERROR] Invalid room code. Use: {list(self.rooms.keys())}")
                        continue

                    if light_num < 1 or light_num > 4:
                        print("[ERROR] Light number must be 1-4")
                        continue

                    if self.send_light_command(room_code, light_num, cmd):
                        print(f"[OK] Light {light_num} in {self.rooms[room_code]} turned {cmd.upper()}")

                elif cmd == 'batch_off':
                    if self.send_batch_off():
                        print("[OK] Batch-off sent")

                elif cmd == 'batch_cont':
                    duration = 5  # default
                    if len(parts) >= 2:
                        try:
                            duration = int(parts[1])
                        except ValueError:
                            print("[ERROR] Duration must be integer")
                            continue

                    if self.send_batch_off_continuous(duration=duration):
                        print("[OK] Batch-off continuous complete")

                else:
                    print(f"[ERROR] Unknown command: {cmd}")
                    print("Type 'menu' for help")

        except KeyboardInterrupt:
            print("\n\n[EXIT] Interrupted by user")
        finally:
            self.disconnect()


if __name__ == '__main__':
    tester = LightTester()
    tester.run()
