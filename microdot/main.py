import network
import time
from microdot import Microdot

# Access point settings
AP_SSID = "MICRODOT-DEMO"

def start_access_point():
    """Configure device as access point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, security=0)  # Open AP
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f"Access Point active: {AP_SSID}")
    print(f"IP address: {ap.ifconfig()[0]}")
    return ap

# Create the Microdot app
app = Microdot()

@app.route('/')
def index(request):
    return "Hello from Microdot!"

# Start AP and run web server
if __name__ == '__main__':
    ap = start_access_point()
    print("Starting web server...")
    app.run(port=80) 

    import gc
    print("Memory Free:", gc.mem_free())
    gc.collect()  # run garbage collection to free ram
    print("Memory Free:", gc.mem_free())



