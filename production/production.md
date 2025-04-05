# PRODUCTION

## Update prod/xwkbot-pcb-v1 with changes from main dir
  - delete old, .cursorrules etc
  - TODO: rsync

## Flash manually

esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash -z 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin

cd xkwbot-pcb-v1
#ampy --port /dev/ttyUSB0 put xkwbot-pcb-v1/ /
mpremote connect /dev/ttyUSB0 cp -r . :
cd ..

## Create and Flash Firmware

Faster (~30 sec instead of 1m+)

esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 read_flash 0x0 0x400000 dump.bin

esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 dump.bin





# OLD
- run `./prod.sh`
