import gc
import asyncio
from microdot import Microdot, Response
from microdot.utemplate import Template
from lib.wlanmanager import WLANManager

# Create the Microdot app
app = Microdot()
Response.default_content_type = 'text/html'

# Initialize template system
Template.initialize(template_dir='templates')

# Add after-request handler for garbage collection
@app.after_request
def cleanup(request, response):
    print("after request: Garbage collection")
    gc.collect()
    return response

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
    
    # Initialize WiFi manager with custom project name
    wlan = WLANManager(app, project_name="MYPROJECT")
    
    # This will either connect to saved WiFi or start AP mode
    if wlan.connect():
        print("Network setup complete, starting web server...")
        
        try:
            # Start web server
            server = asyncio.create_task(app.start_server(host='0.0.0.0', port=80, debug=True))
            
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



