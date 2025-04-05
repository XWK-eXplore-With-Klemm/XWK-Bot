#!/bin/bash

set -e

echo "Erasing flash"
time esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
echo

echo "Flashing Micropython firmware"
time esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash -z 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin
echo

echo "Sleeping..."
sleep 3
echo

echo "Uploading XWK-Bot project files"
cd xkwbot-pcb-v1
#ampy --port /dev/ttyUSB0 put xkwbot-pcb-v1/ /
time mpremote connect /dev/ttyUSB0 cp -r . :
cd ..
echo

echo Done!
echo
