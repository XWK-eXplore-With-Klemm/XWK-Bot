#XWK-BOT 

Website with manual etc: https://xwk.ull.at

For WeMos LOLIN D32 ESP32 WROOM 32

# TODO
- Captive portal
- Timeout WLAN connect if at other place

# Flash Micropython

- Download latest version from https://micropython.org/download/ESP32_GENERIC/
- wget https://micropython.org/resources/firmware/ESP32_GENERIC-20241129-v1.24.1.bin
- esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
- esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash -z 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin


# Command line tools (for AI)

Upload files:
```bash
ampy --port /dev/ttyUSB0 put lib/bot.py /lib/bot.py
```

Reset ESP32:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 run
```

# Web-IDE Projekt
https://github.com/vsolina/micropython-web-editor/tree/development
