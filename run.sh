#!/bin/sh

SHARE_DIR=/share/kocom
CONFIG_DIR=/data

# Create directories if they don't exist
mkdir -p $SHARE_DIR

# Setup configuration file
if [ ! -f $SHARE_DIR/kocom.conf ]; then
    if [ -f /kocom.conf ]; then
        cp /kocom.conf $SHARE_DIR/
        echo "[Info] Created default configuration file at $SHARE_DIR/kocom.conf"
        echo "[Info] Please edit this file to match your setup:"
        echo "[Info]   - RS485 type: serial or socket"
        echo "[Info]   - For socket: update socket_server IP and socket_port"
        echo "[Info]   - For serial: update serial_port (e.g., /dev/ttyUSB0)"
        echo "[Info]   - MQTT settings: server IP, username, password"
    fi
fi

# Copy Python script to share directory (always update to latest)
cp /kocom.py $SHARE_DIR/

echo "[Info] Starting Kocom Wallpad RS485 Integration v2025.01.004 for 덕계역금강펜트리움"
echo "[Info] Python version: $(python3 --version)"
echo "[Info] Configuration directory: $SHARE_DIR"

# Display current configuration
echo "[Info] Current RS485 configuration:"
grep -E "^type|^socket_server|^socket_port|^serial_port" $SHARE_DIR/kocom.conf | sed 's/^/[Info]   /'

# Change to working directory
cd $SHARE_DIR

# Run the main application with auto-restart on failure
while true; do
    python3 -u $SHARE_DIR/kocom.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[Info] Application exited normally"
        break
    else
        echo "[Warning] Application exited with code $EXIT_CODE, restarting in 60 seconds..."
        echo "[Warning] Check configuration at $SHARE_DIR/kocom.conf"
        sleep 60
    fi
done
