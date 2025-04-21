# INSTALL

## FLASH MICROPYTHON
- Download latest version from https://micropython.org/download/ESP32_GENERIC/
- wget https://micropython.org/resources/firmware/ESP32_GENERIC-20241129-v1.24.1.bin
- esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
- esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash -z 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin

## UPLOAD/UPDATE PROJECT FILES

- Install Thonny IDE from https://thonny.org/
- Unzip the project zip file e.g. into "Documents\pixel_painter\"
- Open Thonny IDE

- In the "Files" sidebar navigate to the project folder e.g. "Documents\pixel_painter\"

- Connect to the Pixel Painter via USB
- Click red icon "STOP" to connect to the device
- Maybe you need to press "CTRL-C" to interrupt any running code
- The current files on the Pixel Painter should now appear in the "MicroPython device" sidebar

- Select all files and folders in the "File" sidebar. Select the first one, then hold down SHIFT and select the last one.
- If you have files that you do not want to overwrite like WiFi "config.json", you can deselect them by holding down "CTRL" and clicking on them
- Right click into the selection and select "Upload to /"
- Accept overwrite warnings
- Turn the Pixel Painter off and on again (or press the reset button on the ESP32 microcontroller)


# SETUP WIFI
- Turn on the Pixel Painter
- Connect with your PC/tablet/phoneLook to Wifi PIX_... e.g. PIX_7D80
- If your're device asks if you want to use this connection which has no internet access, select "yes"
- Find your assigned IP in the Wifi network (e.g. 192.168.4.2)
  - Android: just click on the Wifi name and it will show the IP
  - iOS: click on the Wifi name and it will show the IP
  - Windows: open cmd and type "ipconfig" and find "Wi-Fi"
  - MacOS: open terminal and type "ipconfig getifaddr en0"
- Now enter this ip in your browser but with "1" after the last dot: e.g. "http://192.168.4.1"
- Configure your WiFi


# START WEB CODE EDITOR (WEB-IDE)
- Turn on the Pixel Painter
- Read and note the displayed IP-address (green) e.g. "192.168.1.188"
- Enter this ip in your browser: e.g. "http://192.168.1.188"

