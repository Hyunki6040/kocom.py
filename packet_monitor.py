#!/usr/bin/env python3
"""
Kocom Wallpad RS485 Packet Monitor
This tool helps capture and analyze RS485 packets from your Kocom wallpad
"""

import socket
import time
import sys
from datetime import datetime

def hex_to_ascii(hex_string):
    """Convert hex string to ASCII if printable"""
    try:
        hex_bytes = bytes.fromhex(hex_string.replace(' ', ''))
        ascii_str = ""
        for byte in hex_bytes:
            if 32 <= byte <= 126:
                ascii_str += chr(byte)
            else:
                ascii_str += f"[{byte:02x}]"
        return ascii_str
    except:
        return ""

def analyze_packet(hex_data):
    """Analyze Kocom RS485 packet structure"""
    if not hex_data or len(hex_data) < 10:
        return None
    
    hex_bytes = hex_data.replace(' ', '')
    
    # Check for AA55 header and 0D0D trailer
    if not (hex_bytes.startswith('aa55') and hex_bytes.endswith('0d0d')):
        return None
    
    try:
        # Parse packet structure
        analysis = {
            'header': hex_bytes[0:4],  # AA55
            'type': hex_bytes[4:8],    # Type (30BC, 30BD, etc)
            'device': hex_bytes[8:12],  # Device code
            'room': hex_bytes[12:14],   # Room number
            'command': hex_bytes[14:16], # Command
            'data': hex_bytes[16:-8],   # Data payload
            'checksum': hex_bytes[-8:-4], # Checksum
            'trailer': hex_bytes[-4:]   # 0D0D
        }
        
        # Device type mapping
        device_types = {
            '000e': 'Light',
            '002c': 'Gas',
            '0036': 'Thermostat',
            '0039': 'AC',
            '003b': 'Outlet/Plug',
            '0044': 'Elevator',
            '0048': 'Fan',
            '0098': 'Air Quality'
        }
        
        # Room mapping
        rooms = {
            '00': 'All/Main',
            '01': 'Living Room',
            '02': 'Room 1',
            '03': 'Room 2',
            '04': 'Room 3',
            '05': 'Kitchen'
        }
        
        device_name = device_types.get(analysis['device'], f"Unknown({analysis['device']})")
        room_name = rooms.get(analysis['room'], f"Room {analysis['room']}")
        
        return {
            **analysis,
            'device_name': device_name,
            'room_name': room_name
        }
    except:
        return None

def monitor_packets(server_ip, server_port):
    """Connect to EW11 and monitor packets"""
    print(f"\n🔍 Kocom RS485 Packet Monitor")
    print(f"📡 Connecting to {server_ip}:{server_port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        print(f"✅ Connected successfully!\n")
        print("=" * 80)
        print("Monitoring packets... Press buttons on your wallpad to capture packets")
        print("Press Ctrl+C to stop")
        print("=" * 80 + "\n")
        
        buffer = ""
        packet_count = 0
        
        while True:
            data = sock.recv(1024)
            if not data:
                print("\n❌ Connection lost!")
                break
                
            hex_data = data.hex()
            buffer += hex_data
            
            # Look for complete packets (ending with 0d0d)
            while '0d0d' in buffer:
                end_pos = buffer.index('0d0d') + 4
                packet = buffer[:end_pos]
                buffer = buffer[end_pos:]
                
                # Look for AA55 header
                if 'aa55' in packet:
                    start_pos = packet.index('aa55')
                    packet = packet[start_pos:]
                    
                    packet_count += 1
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    
                    # Format packet for display
                    formatted = ' '.join([packet[i:i+2] for i in range(0, len(packet), 2)])
                    
                    print(f"\n[{timestamp}] Packet #{packet_count}")
                    print(f"RAW: {formatted}")
                    
                    # Analyze packet
                    analysis = analyze_packet(packet)
                    if analysis:
                        print(f"┌─ HEADER: {analysis['header'].upper()} (Kocom)")
                        print(f"├─ TYPE: {analysis['type'].upper()}")
                        print(f"├─ DEVICE: {analysis['device'].upper()} → {analysis['device_name']}")
                        print(f"├─ ROOM: {analysis['room'].upper()} → {analysis['room_name']}")
                        print(f"├─ COMMAND: {analysis['command'].upper()}")
                        print(f"├─ DATA: {analysis['data'].upper()}")
                        print(f"├─ CHECKSUM: {analysis['checksum'].upper()}")
                        print(f"└─ TRAILER: {analysis['trailer'].upper()}")
                        
                        # Specific interpretations
                        if analysis['device'] == '000e':  # Light
                            if analysis['command'] == '01':
                                print(f"   💡 Light ON command")
                            elif analysis['command'] == '00':
                                print(f"   💡 Light OFF command")
                                
                        elif analysis['device'] == '0036':  # Thermostat
                            if len(analysis['data']) >= 2:
                                temp = int(analysis['data'][:2], 16)
                                if temp > 0:
                                    print(f"   🌡️ Temperature: {temp}°C")
                    
                    print("-" * 80)
                    
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        sock.close()
        print("\n📊 Session Summary:")
        print(f"   Total packets captured: {packet_count}")

def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print("Usage: python3 packet_monitor.py <IP_ADDRESS> <PORT>")
        print("Example: python3 packet_monitor.py 192.168.0.222 8899")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    monitor_packets(server_ip, server_port)

if __name__ == "__main__":
    main()