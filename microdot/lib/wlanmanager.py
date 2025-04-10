"""
WiFi configuration manager for Microdot
Handles both station (client) and access point modes with captive portal
"""

import gc
import network
import time
import ubinascii
from iniconf import Iniconf
from microdot import Response

class WLANManager:
    def __init__(self, app, project_name="MICRODOT", config_path="/config.ini"):
        """
        Initialize WiFi manager
        :param app: Microdot app instance to add routes to
        :param project_name: Name used for AP SSID (default: MICRODOT)
        :param config_path: Path to config file (default: /config.ini)
        """
        self.app = app
        self.project_name = project_name
        self.config = Iniconf()
        self.config.set_config_file(config_path)  # Must be called before first get()
        self._register_routes()
        
    def _register_routes(self):
        """Register captive portal routes with the app"""
        
        @self.app.route('/generate_204')  # Android
        @self.app.route('/gen_204')       # Android
        @self.app.route('/ncsi.txt')      # Windows
        @self.app.route('/hotspot-detect.html')  # iOS
        @self.app.route('/library/test/success.html')  # iOS
        async def captive_portal_check(request):
            """Redirect all captive portal detection requests to the index page"""
            return Response(body='', status_code=302, headers={'Location': f'http://{request.host}/'})

        @self.app.route('/connecttest.txt')  # Windows
        async def windows_connect_test(request):
            """Return Microsoft Connect Test response"""
            return "Microsoft Connect Test"

        @self.app.route('/fwlink')  # Windows
        async def windows_redirect(request):
            """Redirect Windows captive portal requests"""
            return Response.redirect('/')

        @self.app.route('/wifi')
        async def wifi_config(request):
            """Serve WiFi configuration page"""
            networks = self._scan_networks()
            network_options = "".join([
                f'<option value="{ssid}">{ssid}</option>'
                for ssid in networks
            ])
            
            return f"""
            <html><head>
                <title>{self.project_name} WiFi Setup</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial; margin: 20px; }}
                    select, input {{ margin: 10px 0; padding: 5px; width: 200px; }}
                    form {{ max-width: 300px; margin: 0 auto; }}
                </style>
            </head><body>
                <h1>{self.project_name} WiFi Setup</h1>
                <form method="POST" action="/wifi">
                    <select name="ssid" required>
                        <option value="">Select Network...</option>
                        {network_options}
                    </select><br>
                    <input type="text" name="password" placeholder="Password" required><br>
                    <input type="submit" value="Connect">
                </form>
            </body></html>
            """

        @self.app.route('/wifi', methods=['POST'])
        async def wifi_config_post(request):
            """Handle WiFi configuration form submission"""
            form = request.form
            ssid = form.get('ssid')
            password = form.get('password')
            
            if ssid and password:
                print(f"Saving WiFi configuration: {ssid}")
                self.config.set('WLAN_SSID', ssid)
                self.config.set('WLAN_PASSWORD', password)
                self.config.save()
                
                # Schedule restart
                async def _restart():
                    await asyncio.sleep(2)
                    import machine
                    machine.reset()
                
                asyncio.create_task(_restart())
                
                return f"""
                <html><head>
                    <title>Configuration Saved</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {{ font-family: Arial; margin: 20px; text-align: center; }}
                    </style>
                </head><body>
                    <h1>Configuration Saved!</h1>
                    <p>The device will now restart and try to connect to the selected network.</p>
                </body></html>
                """
            
            return Response.redirect('/wifi')

    def _scan_networks(self):
        """Scan for available WiFi networks"""
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        time.sleep(1)
        
        networks = []
        for _ in range(3):  # Try scanning up to 3 times
            try:
                scan_result = sta_if.scan()
                networks = [net[0].decode('utf-8') for net in scan_result if net[0]]
                if networks:
                    break
            except:
                pass
            time.sleep(1)
        
        return sorted(set(networks))  # Remove duplicates and sort

    def start_ap(self):
        """Start access point mode"""
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(0.1)
        ap.active(True)
        
        # Get last 4 characters of MAC address
        sta_if = network.WLAN(network.STA_IF)
        mac = ubinascii.hexlify(sta_if.config('mac')).decode()
        ap_ssid = f"{self.project_name}_{mac[-4:].upper()}"
        
        ap.config(essid=ap_ssid,
                 authmode=network.AUTH_OPEN,
                 channel=1,
                 hidden=False)
        
        print("Access Point active!")
        print(f"SSID: {ap_ssid}")
        print(f"Configuration URL: http://{ap.ifconfig()[0]}/wifi")
        
        return True

    def connect(self):
        """
        Try to connect to configured WiFi network
        Returns True if connected, False if AP mode started
        """
        ssid = self.config.get('WLAN_SSID')
        password = self.config.get('WLAN_PASSWORD')
        
        if not ssid or not password:
            print("No valid WiFi configuration found")
            return self.start_ap()

        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            if not wlan.isconnected():
                print(f"Connecting to WiFi: {ssid}")
                wlan.connect(ssid, password)

                start_time = time.time()
                while not wlan.isconnected() and time.time() - start_time < 30:
                    time.sleep(0.2)

            if wlan.isconnected():
                print("Successfully connected to WiFi")
                print(f"IP: {wlan.ifconfig()[0]}")
                return True
                
            print("Could not connect to WiFi")
            return self.start_ap()
            
        except Exception as e:
            print("WiFi connection error:", e)
            return self.start_ap() 