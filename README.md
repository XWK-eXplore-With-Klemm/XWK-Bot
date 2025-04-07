# XWK-Bot

https://github.com/XWK-eXplore-With-Klemm/XWK-Bot

Website with manual etc: https://xwk.ull.at


## Troubleshooting

import gc
print("Memory Free:", gc.mem_free())
print("Memory Allocated:", gc.mem_alloc())
print("Memory Total:", gc.mem_free() + gc.mem_alloc())
gc.collect()  # Force garbage collection
print("Memory after GC:", gc.mem_free())


## Upload file

 mpremote cp micropython/lib/ota.py :/lib/


 #XWK-BOT 

Website with manual etc: https://xwk.ull.at

Github repo: https://github.com/XWK-eXplore-With-Klemm/XWK-Bot

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

https://docs.micropython.org/en/latest/reference/mpremote.html

Upload files:
```bash
ampy --port /dev/ttyUSB0 put lib/bot.py /lib/bot.py
mpremote cp micropython/lib/ota.py :/lib/
```

Reset ESP32:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 run
```

# Web-IDE Projekt
https://github.com/vsolina/micropython-web-editor/tree/development


# mpremote

https://docs.micropython.org/en/latest/reference/mpremote.html

`resume` prevents soft-reset of the device. e.g. `mpremote resume fs ls`