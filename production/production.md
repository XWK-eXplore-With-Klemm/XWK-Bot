# PRODUCTION

This describes how to flash new ESPs.


## Flash a single device with latest code:

- ota/ota.sh        # Create up to date filelist.json und upload to http server
- git commit
- production/production.sh

## Special setups (e.g. for Elisa school)
- create separate branch ?
- configure wlan in config.ini
- generate_filelist.sh comment in the unwanted demo programs 


## Create image

esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 read_flash 0x0 0x400000 production/image.bin

## Mass flash ESPs

Faster than production.sh (~30 sec instead of 1m+)
TODO: it seems not everything is overwritten, a wifi config was still retained ??? So only use for fresh ESPs?

time esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 production/image.bin
