#!/bin/sh

SHARE_DIR=/share/kocom
CONFIG_DIR=/data

# Create directories if they don't exist
mkdir -p $SHARE_DIR

# Setup configuration file
if [ ! -f $SHARE_DIR/kocom.conf ]; then
    if [ -f /kocom.conf ]; then
        cp /kocom.conf $SHARE_DIR/
    fi
fi

# Copy Python script to share directory (always update to latest)
cp /kocom.py $SHARE_DIR/

echo "[Info] Starting Kocom Wallpad RS485 Integration v2025.01.001"
echo "[Info] Python version: $(python3 --version)"
echo "[Info] Configuration directory: $SHARE_DIR"

# Change to working directory
cd $SHARE_DIR

# Run the main application with proper error handling
exec python3 -u $SHARE_DIR/kocom.py
