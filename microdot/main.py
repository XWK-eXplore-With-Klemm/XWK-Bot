# main.py
gc.collect()
print("Memory after startup collect:", gc.mem_free())

"""
from iniconf import Iniconf
config = Iniconf()
ssid = config.get('WLAN_SSID')
password = config.get('WLAN_PASSWORD')
print(ssid)
print(password)

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(str(ssid), str(password))


if wlan.isconnected():
    print("Successfully connected to WiFi")
else:
    print("Failed to connect to WiFi")

"""

#global placeholder_blocks
#placeholder_blocks = [bytearray(45000)]  # 45 KB reserved

# gc.collect()
# print("Memory after placeholder blocks:", gc.mem_free())

import bot
bot.write("Starting XWK-Bot...", color=bot.WHITE)

import gc
from lib.wlanmanager import WlanManager
from lib.wlan_manager_ui_bot import WlanManagerUiBot

print("Memory at start of main:", gc.mem_free())
gc.collect()
print("Memory after GC:", gc.mem_free())

# Initialize WiFi manager with Bot-specific UI handler
wlan = WlanManager(ui=WlanManagerUiBot(), project_name="XWK-BOT")
#wlan = WlanManager(project_name="XWK-BOT")

# Free placeholder before AP mode
# print("Memory before placeholder removal:", gc.mem_free())
# del placeholder_blocks
# gc.collect()
# print("Memory after placeholder removal:", gc.mem_free())

#wlan.start_ap()

#First try to connect - this is lightweight and uses minimal RAM
if not wlan.connect():
    print("WiFi connection failed, starting AP mode...")
    # Only now load the heavy AP mode dependencies
    wlan.start_ap()  # This will now start the web server internally

print("Setup complete")



