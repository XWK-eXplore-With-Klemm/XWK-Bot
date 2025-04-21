# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

print("Activating network")
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ullwpa', 'oldenburg')

if wlan.isconnected():
    print("Successfully connected to WiFi")
else:
    print("Failed to connect to WiFi")
    
print("Starting IDE web editor service")

print("Starting webrepl")
import webrepl
webrepl.start()

print("Starting IDE web service")
import weditor.start