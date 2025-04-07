#!/bin/bash
set -e

# Script to configure WiFi on an ESP32 using config.local.ini and iniconf.py
# Reads WLAN_SSID and WLAN_PASSWORD from config.local.ini and updates config.ini on the device

# Check if config.local.ini exists
if [ ! -f "config.local.ini" ]; then
    echo "Error: config.local.ini not found in current directory"
    exit 1
fi

# Extract WiFi credentials from config.local.ini
WLAN_SSID=$(grep "WLAN_SSID=" config.local.ini | cut -d'=' -f2 | tr -d ' ')
WLAN_PASSWORD=$(grep "WLAN_PASSWORD=" config.local.ini | cut -d'=' -f2 | tr -d ' ')

if [ -z "$WLAN_SSID" ] || [ -z "$WLAN_PASSWORD" ]; then
    echo "Error: WLAN_SSID or WLAN_PASSWORD not found in config.local.ini"
    exit 1
fi

echo "Configuring WiFi for SSID: $WLAN_SSID"

# Configure WiFi settings in config.ini on the device using iniconf
echo "Updating config.ini on device with WiFi settings..."
mpremote exec "
from lib.iniconf import Iniconf
config = Iniconf()
config.set('WLAN_SSID', '$WLAN_SSID')
config.set('WLAN_PASSWORD', '$WLAN_PASSWORD')
config.save()
import machine
machine.soft_reset()
"

echo "WiFi configuration complete!"
echo "You may need to reset the device for changes to take effect."
echo "Done!"