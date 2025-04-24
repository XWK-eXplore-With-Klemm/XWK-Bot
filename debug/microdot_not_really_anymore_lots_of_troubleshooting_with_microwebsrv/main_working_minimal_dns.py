# main.py
gc.collect()
print("Memory after startup collect:", gc.mem_free())

import network
import time
import gc
from lib.phew import dns
import uasyncio

ap = network.WLAN(network.AP_IF)
ap.active(False)
time.sleep(0.1)
ap.active(True)

ap.config(essid="XWK-BOT",
            authmode=network.AUTH_OPEN,
            channel=1,
            hidden=False)
        
# Get AP IP and notify UI before loading web dependencies
ip = ap.ifconfig()[0]
print(f"AP IP: {ip}")

gc.collect()
print("Memory after AP:", gc.mem_free())

print("Starting DNS server for captive portal...")
dns.run_catchall(ip)

gc.collect()
print("Memory after DNS:", gc.mem_free())

# Keep the script running and handle events
print("Starting event loop...")
try:
    loop = uasyncio.get_event_loop()
    loop.run_forever()
except Exception as e:
    print(f"Error in event loop: {e}")
finally:
    print("Event loop stopped")

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
"""



