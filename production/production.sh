#!/bin/bash
set -e

# Check for --no-flash flag
NO_FLASH=false
for arg in "$@"; do
    if [ "$arg" = "--no-flash" ]; then
        NO_FLASH=true
        break
    fi
done

# (Re-flash) the ESP32 board while using OTA update functionality with builtin features (blacklist...)
# Run from project root
# These needs a valid wlan configuration in config.local.ini (WLAN_SSID, WLAN_PASSWORD)

if [ "$NO_FLASH" = false ]; then
    echo "If flashing fails, try reset button on the board and immediately start the script again!"
    echo 

    echo "Erasing flash"
    esptool.py --chip esp32 erase_flash
    echo

    echo "Flashing Micropython firmware"
    # Download latest version from https://micropython.org/download/ESP32_GENERIC/
    # mpremote reset --bootloader;
    esptool.py --chip esp32 --baud 921600 write_flash -z 0x1000 production/ESP32_GENERIC-20241129-v1.24.1.bin
    echo

    echo "Waiting 3 seconds for device to settle..."
    sleep 3
    echo
fi

#echo "Uploading XWK-Bot project files"
#cd xkwbot-pcb-v1
##ampy --port /dev/ttyUSB0 put xkwbot-pcb-v1/ /
#time mpremote connect /dev/ttyUSB0 cp -r . :
#cd ..
#echo

# WLAN didn't connect with mode --no-flash here...
echo "Deleting boot.py file if it exists..."
mpremote resume fs rm boot.py || true
echo

echo "Resetting device..."
mpremote reset
echo

echo "Setting up WiFi..."
WLAN_SSID=$(grep "WLAN_SSID=" config.local.ini | cut -d'=' -f2)
WLAN_PASSWORD=$(grep "WLAN_PASSWORD=" config.local.ini | cut -d'=' -f2)
mpremote resume exec "
import network
import time

# First check if AP mode is active and disable it
ap = network.WLAN(network.AP_IF)
if ap.active():
    print('Access Point mode is active, disabling...')
    ap.active(False)
    time.sleep(1)

# Now setup station mode
wlan = network.WLAN(network.STA_IF)
# First disconnect and deactivate to ensure clean connection
wlan.disconnect()
wlan.active(False)
time.sleep(1)
print('Activating new network...')
wlan.active(True)
print(f'Connecting to SSID: {\"$WLAN_SSID\"}...')
wlan.connect('$WLAN_SSID', '$WLAN_PASSWORD')

# Wait for connection
while not wlan.isconnected():
    print('Waiting for connection...')
    time.sleep(1)
print('WiFi Status: Connected' if wlan.isconnected() else 'WiFi Status: Not Connected')
print(f'IP Address: {wlan.ifconfig()[0]}' if wlan.isconnected() else 'IP Address: None')
"

echo "Starting OTA update..."
mpremote resume cp micropython/config.ini :/
mpremote resume fs mkdir lib || true
mpremote resume cp micropython/lib/iniconf.py :/lib/
mpremote resume cp micropython/lib/ota.py :/lib/
mpremote resume exec "from lib.ota import OTAUpdater; updater = OTAUpdater(); updater.update_all()"
echo 

echo "Resetting device..."
mpremote resume reset           # resume prevents soft-reset of the device, otherwise the device would reset twice
echo

echo Done!
echo
