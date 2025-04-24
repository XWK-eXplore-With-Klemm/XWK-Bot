import network
import time
import phew.server as server
from phew.dns import run_catchall

# Access point settings
AP_SSID = "PHEW-DEMO"
AP_DOMAIN = "phew.local"

def start_access_point():
    """Start access point and serve welcome page"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, security=0)  # Open AP
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f"Access Point active: {AP_SSID}")
    print(f"IP address: {ap.ifconfig()[0]}")
    
    # Start the DNS server
    run_catchall(ap.ifconfig()[0])
    
    # Define routes
    @server.route("/", methods=["GET"])
    # template does not work:
    # def index(request):
    #     """Serve welcome page from template"""
    #     return render_template("templates/index.html", ssid=AP_SSID)


    def index(request):
        """Serve welcome page"""
        return "<h1>Hello</h1>"
    
    # Start the web server
    print("Starting web server...")
    server.run()

if __name__ == "__main__":
    print("Starting Access Point mode...")
    start_access_point() 