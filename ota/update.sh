#!/bin/bash

# Script to set up WiFi and perform OTA update
# Usage: ./ota/update.sh

# Check if config.local.ini exists
if [ ! -f "config.local.ini" ]; then
    echo "Error: config.local.ini not found"
    exit 1
fi

# Read WiFi credentials from config.local.ini
WLAN_SSID=$(grep "WLAN_SSID=" config.local.ini | cut -d'=' -f2)
WLAN_PASSWORD=$(grep "WLAN_PASSWORD=" config.local.ini | cut -d'=' -f2)

# Check if credentials were found
if [ -z "$WLAN_SSID" ] || [ -z "$WLAN_PASSWORD" ]; then
    echo "Error: WiFi credentials not found in config.local.ini"
    exit 1
fi

# Set up WiFi using mpremote
echo "Setting up WiFi connection..."
mpremote exec "
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('$WLAN_SSID', '$WLAN_PASSWORD')

# Wait for connection
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('Network connection failed')
else:
    print('Connected to WiFi')
    print('IP:', wlan.ifconfig()[0])
"

# Check if WiFi setup was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up WiFi connection"
    exit 1
fi

# Proceed with OTA update
echo "Starting OTA update..."
# Add your OTA update commands here 