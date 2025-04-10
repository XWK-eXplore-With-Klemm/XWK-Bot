import network
import time
import gc
import asyncio
from microdot import Microdot, Response
from microdot.utemplate import Template
from lib.phew import dns

# Access point settings
AP_SSID = "MICRODOT-DEMO"
AP_IP = "192.168.4.1"
AP_DOMAIN = "esp32.wifi"

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

# Add after-request handler for garbage collection
# This does not make much difference
# @app.after_request
# def cleanup(request, response):
#     print("after request: Garbage collection")
#     gc.collect()
#     return response

@app.route('/')
async def index(request):
    gc.collect()
    mem_free = gc.mem_free()
    return Template('index.html').render(mem_free=mem_free)

# Captive Portal Routes
@app.route('/generate_204')  # Android
@app.route('/gen_204')       # Android
@app.route('/ncsi.txt')      # Windows
@app.route('/hotspot-detect.html')  # iOS
@app.route('/library/test/success.html')  # iOS
async def captive_portal_check(request):
    """Redirect all captive portal detection requests to the index page"""
    #return Response.redirect('/')
    # This prevents error "  File "microdot/microdot.py", line 1334, in handle_request | File "microdot/microdot.py", line 392, in create | UnicodeError: "
    return Response(body='', status_code=302, headers={'Location': f'http://{AP_IP}/'})

@app.route('/connecttest.txt')  # Windows
async def windows_connect_test(request):
    """Return Microsoft Connect Test response"""
    return "Microsoft Connect Test"

@app.route('/fwlink')  # Windows
async def windows_redirect(request):
    """Redirect Windows captive portal requests"""
    return Response.redirect('/')

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
    print("Starting DNS and web server...")
    
    try:
        # Start DNS server
        dns.run_catchall(AP_IP)
        
        # Start web server in background
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



