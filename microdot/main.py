import gc
import asyncio
from microdot import Microdot, Response
from microdot.utemplate import Template
from lib.wlanmanager import WlanManager
from lib.wlan_manager_ui_bot import WlanManagerUiBot

# Create the Microdot instance
microdot = Microdot()
Response.default_content_type = 'text/html'

# Initialize template system
Template.initialize(template_dir='templates')

# Add after-request handler for garbage collection
@microdot.after_request
def cleanup(request, response):
    print("after request: Garbage collection")
    gc.collect()
    print("Memory after GC:", gc.mem_free())
    return response

@microdot.route('/')
async def index(request):
    gc.collect()
    mem_free = gc.mem_free()
    return Template('index.html').render(mem_free=mem_free)

@microdot.route('/memory')
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
    
    # Initialize WiFi manager with Bot-specificUI handler
    wlan = WlanManager(microdot, ui=WlanManagerUiBot(), project_name="XWK-BOT")
    
    # First try to connect - this is lightweight and uses minimal RAM
    # as it doesn't load the AP mode dependencies
    if not wlan.connect():
        print("WiFi connection failed, starting AP mode...")
        # Only now load the heavy AP mode dependencies (microdot routes, dns server, etc)
        wlan.start_ap()
    
    print("Network setup complete, starting web server...")
    
    try:
        # Start web server
        server = asyncio.create_task(microdot.start_server(host='0.0.0.0', port=80, debug=True))
        
        # Here you can add other async tasks if needed
        # For example:
        # other_task = asyncio.create_task(some_other_async_function())
        
        # Wait for the server task
        await server
        
    except KeyboardInterrupt:
        print("Server stopped")
        print("Final memory:", gc.mem_free())

# Start network and run web server
if __name__ == '__main__':
    asyncio.run(main())



