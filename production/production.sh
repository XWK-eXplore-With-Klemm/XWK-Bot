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

echo "Setting up WiFi..."
WLAN_SSID=$(grep "WLAN_SSID=" config.local.ini | cut -d'=' -f2)
WLAN_PASSWORD=$(grep "WLAN_PASSWORD=" config.local.ini | cut -d'=' -f2)
mpremote exec "import network; wlan = network.WLAN(network.STA_IF); wlan.active(True); wlan.connect('$WLAN_SSID', '$WLAN_PASSWORD')"
sleep 2

echo "Starting OTA update..."
mpremote cp micropython/config.ini :/
mpremote fs mkdir lib || true
mpremote cp micropython/lib/ini_parser.py :/lib/
mpremote cp micropython/lib/ota.py :/lib/
mpremote exec "from lib.ota import OTAUpdater; updater = OTAUpdater(); updater.update_all()"

echo Done!
echo
