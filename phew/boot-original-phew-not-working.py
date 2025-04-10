import network
import time
from phew import connect_to_wifi
from phew.template import render_template
import phew.server as server
from phew.dns import run_catchall

# WiFi credentials - replace with your actual credentials
WIFI_SSID = "ullwpa"
WIFI_PASSWORD = "oldenburg"

# Access point configuration
AP_SSID = "PHEW-AP"
#AP_PASSWORD = "12345678"
AP_DOMAIN = "esp32.wifi"

def start_access_point():
    """Start access point mode for WiFi configuration"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    # ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ap.config(essid=AP_SSID, security=0)  # security=0 means no password
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f"Access Point active. Connect to {AP_SSID}")
    print(f"AP IP address: {ap.ifconfig()[0]}")
    
    # Start the DNS server
    run_catchall(ap.ifconfig()[0])
    
    @server.route("/", methods=["GET"])
    def index(request):
        """Serve the WiFi configuration page"""
        return render_template("wifi_config.html")
    
    @server.route("/configure", methods=["POST"])
    def configure(request):
        """Handle WiFi configuration form submission"""
        if "ssid" in request.form and "password" in request.form:
            with open("wifi_config.txt", "w") as f:
                f.write(f"{request.form['ssid']}\n{request.form['password']}")
            return "WiFi configured. Please reset your device."
        return "Missing credentials", 400
    
    # Start the web server
    server.run()

def main():
    """Main function to handle WiFi connection"""
    try:
        # Try to connect to WiFi
        ip_address = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected to WiFi. IP address: {ip_address}")
        
    except Exception as e:
        print(f"Failed to connect to WiFi: {e}")
        print("Starting Access Point mode...")
        start_access_point()

if __name__ == "__main__":
    main()
