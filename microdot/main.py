import network
import time
import gc
import asyncio
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
    return Template('index.html').render(mem_free=mem_free)

@app.route('/memory')
async def memory(request):
    gc.collect()
    return {
        'memory_free': gc.mem_free(),
        'memory_alloc': gc.mem_alloc()
    }

async def main():
    print("Memory before startup:", gc.mem_free())
    gc.collect()
    print("Memory after GC:", gc.mem_free())
    
    ap = start_access_point()
    print("Starting web server...")
    
    try:
        # start the server in a background task
        server = asyncio.create_task(app.start_server(host='0.0.0.0', port=80, debug=True))
        
        # Here you can add other async tasks if needed
        # For example:
        # other_task = asyncio.create_task(some_other_async_function())
        
        # Wait for the server task
        await server
        
    except KeyboardInterrupt:
        print("Server stopped")
        print("Final memory:", gc.mem_free())

# Start AP and run web server
if __name__ == '__main__':
    asyncio.run(main())



