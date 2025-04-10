import network
import time
import gc
from microdot import Microdot, Response
from microdot.utemplate import Template

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
Response.default_content_type = 'text/html'

# Initialize template system
Template.initialize(template_dir='templates')

@app.route('/')
async def index(request):
    gc.collect()
    mem_free = gc.mem_free()
    #return Template('index.html').render(mem_free=mem_free)
    return Template('index.html').render()

@app.route('/memory')
async def memory(request):
    gc.collect()
    return {
        'memory_free': gc.mem_free(),
        'memory_alloc': gc.mem_alloc()
    }

# Start AP and run web server
if __name__ == '__main__':
    print("Memory before startup:", gc.mem_free())
    gc.collect()
    print("Memory after GC:", gc.mem_free())
    
    ap = start_access_point()
    print("Starting web server...")
    
    try:
        app.run(port=80, debug=True)
    except KeyboardInterrupt:
        print("Server stopped")
        print("Final memory:", gc.mem_free())



