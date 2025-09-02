# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kocom Wallpad RS485 integration for Home Assistant. This is a Home Assistant add-on that communicates with Kocom wallpad devices via RS485 serial or socket connection and bridges them to Home Assistant through MQTT.

## Critical Python Compatibility Issue

**IMPORTANT**: The project currently uses Python 3.7 which is incompatible with newer versions of paho-mqtt library:
- Python 3.7 doesn't support `typing.Literal` (added in Python 3.8)
- Latest paho-mqtt requires `typing_extensions` for Python <3.8

### Fix Options:
1. **Add typing_extensions to Dockerfile**: `RUN python3 -m pip install typing_extensions`
2. **Downgrade paho-mqtt**: `RUN python3 -m pip install paho-mqtt==1.5.1`
3. **Upgrade Python base image**: Change `FROM python:3.7.3` to `FROM python:3.10-slim` or newer

## Architecture

### Core Communication Flow
```
Kocom Wallpad <--RS485--> kocom.py <--MQTT--> Home Assistant
```

### Key Components

**kocom.py** - Main application that:
- Manages RS485 serial/socket communication through `RS485Wrapper` class
- Handles MQTT client connection and message routing
- Translates between Kocom protocol (hex packets) and MQTT topics
- Supports multiple device types: lights, thermostats, gas valve, fan, elevator, AC

**RS485 Protocol**:
- Header: `aa55`, Trailer: `0d0d`
- 21-byte packets with checksum at position 18
- Device codes: wallpad(01), light(0e), gas(2c), thermo(36), AC(39), plug(3b), elevator(44), fan(48), air(98)

## Build and Run Commands

### Local Development
```bash
# Build Docker image
docker build -t kocom-wallpad .

# Run container (requires config in /share/kocom/)
docker run -v /path/to/share:/share kocom-wallpad
```

### Home Assistant Add-on Installation
1. Add repository URL: `https://github.com/vifrost/kocom.py`
2. Install "Kocom Wallpad with RS485" add-on
3. Configure `/share/kocom/kocom.conf`
4. Start add-on

### Testing
```bash
# Test RS485 connection
python3 kocom.py  # Reads config from kocom.conf

# Monitor MQTT messages
mosquitto_sub -h [mqtt_server] -p 1883 -t 'kocom/#' -v
```

## Configuration

Main configuration file: `kocom.conf`

### Key Sections:
- **[RS485]**: Connection type (serial/socket), port settings
- **[MQTT]**: Server address, port, authentication
- **[Device]**: List of enabled devices (e.g., `light_livingroom`, `thermo_room1`)
- **[Elevator]**: Type (rs485/tcpip), floor settings
- **[User]**: Initial temperatures, fan modes, device counts

### Device Naming Convention:
- Single device: `devicetype` (e.g., `fan`, `elevator`)
- Multiple devices: `devicetype_roomname` (e.g., `light_room1`, `thermo_livingroom`)
- Supported rooms: `myhome`, `livingroom`, `room1`, `room2`, `room3`, `kitchen`

## MQTT Topics Structure

### Command Topics:
- `kocom/{devicetype}/command` - For single devices
- `kocom/{devicetype}/{room}/command` - For room-specific devices

### State Topics:
- `kocom/{devicetype}/state` - Device state updates
- `kocom/{devicetype}/{room}/state` - Room-specific state

### Supported Commands:
- Lights: `on`, `off`
- Thermostat: Temperature setting, on/off
- Fan: Speed modes (low/medium/high)
- Elevator: Call command

## Common Development Tasks

### Fix Python Compatibility Issue
```bash
# Edit Dockerfile to add typing_extensions
echo "RUN python3 -m pip install typing_extensions" >> Dockerfile

# Or downgrade paho-mqtt
sed -i 's/paho-mqtt/paho-mqtt==1.5.1/' Dockerfile
```

### Add New Device Type
1. Add device code to `device_t_dic` dictionary in kocom.py
2. Implement packet handling in main loop
3. Add MQTT command/state handlers
4. Update config.yaml if needed

### Debug RS485 Communication
1. Enable debug logging in kocom.conf:
   ```ini
   show_query_hex = True
   show_recv_hex = True
   ```
2. Check logs for hex packet dumps
3. Verify checksum calculations

### Update Home Assistant Add-on Version
1. Edit `config.yaml` version field
2. Update CHANGELOG.md
3. Push to GitHub repository
4. Reinstall add-on in Home Assistant

## Important Notes

- The add-on maps `/share` directory for persistent configuration
- Serial port access requires `uart: true` in config.yaml
- Socket connections supported for network-based RS485 adapters
- Elevator TCP/IP mode is experimental and risky - avoid unless necessary
- Polling interval default is 300 seconds (5 minutes)
- 매번 changelog와 readme를 관리해. changelog는 오늘 날짜를 확인해서 major 업데이트만 기록해. 단순 버그 픽스들은 기록할 필요 없어.