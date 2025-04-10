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
from microdot.utemplate import Template

class WLANManager:
    def __init__(self, microdot, project_name="MICRODOT", config_path="/config.ini"):
        """
        Initialize WiFi manager
        :param microdot: Microdot instance to add routes to
        :param project_name: Name used for AP SSID (default: MICRODOT)
        :param config_path: Path to config file (default: /config.ini)
        """
        self.microdot = microdot
        self.project_name = project_name
        self.config = Iniconf()
        self.config.set_config_file(config_path)

    def connect(self):
        """
        Try to connect to configured WiFi network
        Returns True if connected, False if connection failed
        """
        gc.collect()  # Clean up before starting
        print("Memory before WiFi:", gc.mem_free())
        
        ssid = self.config.get('WLAN_SSID')
        password = self.config.get('WLAN_PASSWORD')
        
        if not ssid or not password:
            print("No valid WiFi configuration found")
            return False

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
                gc.collect()
                print("Memory after WiFi connection:", gc.mem_free())
                return True
                
            print("Could not connect to WiFi")
            return False
            
        except Exception as e:
            print("WiFi connection error:", e)
            return False

    def start_ap(self):
        """Start access point mode with configuration portal"""
        # Only import heavy dependencies when AP mode is actually needed
        import machine
        from microdot import Response
        from lib.phew import dns
        
        # Register routes for the captive portal
        self._register_routes()
        
        # Start AP mode
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
        
        # Start DNS server for captive portal
        ip = ap.ifconfig()[0]
        dns.run_catchall(ip)
        
        print("Access Point active!")
        print(f"SSID: {ap_ssid}")
        print(f"Configuration URL: http://{ip}/wifi-config")
        
        return True

    def _register_routes(self):
        """Register captive portal routes with microdot"""
        from microdot import Response  # Only imported when needed
        
        @self.microdot.route('/generate_204')  # Android
        @self.microdot.route('/gen_204')       # Android
        @self.microdot.route('/ncsi.txt')      # Windows
        @self.microdot.route('/hotspot-detect.html')  # iOS
        @self.microdot.route('/library/test/success.html')  # iOS
        async def captive_portal_check(request):
            """Redirect all captive portal detection requests to the index page"""
            ap = network.WLAN(network.AP_IF)
            ip = ap.ifconfig()[0]
            return Response(body='', status_code=302, headers={'Location': f'http://{ip}/wifi-config'})

        @self.microdot.route('/connecttest.txt')  # Windows
        async def windows_connect_test(request):
            """Return Microsoft Connect Test response"""
            return "Microsoft Connect Test"

        @self.microdot.route('/fwlink')  # Windows
        async def windows_redirect(request):
            """Redirect Windows captive portal requests"""
            return Response.redirect('/wifi-config')

        @self.microdot.route('/wifi-config')
        async def wifi_config(request):
            """Serve WiFi configuration page"""
            networks = self._scan_networks()
            return Template('wlanmanager_config.html').render(
                project_name=self.project_name,
                networks=networks
            )

        @self.microdot.route('/wifi-config', methods=['POST'])
        async def wifi_config_post(request):
            """Handle WiFi configuration form submission"""
            import machine
            import asyncio  # Import here where it's actually used
            
            form = request.form
            ssid = form.get('ssid')
            password = form.get('password')
            
            if ssid and password:
                print(f"Saving WiFi configuration: {ssid}")
                try:
                    self.config.set('WLAN_SSID', ssid)
                    self.config.set('WLAN_PASSWORD', password)
                    self.config.save()
                    
                    # Schedule restart after response is sent
                    async def _restart():
                        await asyncio.sleep(2)
                        machine.reset()
                    
                    asyncio.create_task(_restart())
                    
                    return Template('wlanmanager_success.html').render()
                    
                except Exception as e:
                    print(f"Error saving config: {e}")
                    return Template('wlanmanager_error.html').render(error=str(e))
            
            return Response.redirect('/wifi-config')

    def _scan_networks(self):
        """Scan for available WiFi networks and sort by signal strength"""
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        time.sleep(1)
        
        networks = []
        for _ in range(3):  # Try scanning up to 3 times
            try:
                scan_result = sta_if.scan()
                # Each network tuple contains: ssid, bssid, channel, RSSI, security, hidden
                # Convert to list of tuples (ssid, rssi) for sorting
                networks = [(net[0].decode(), net[3]) for net in scan_result if net[0]]
                if networks:
                    break
            except:
                pass
            time.sleep(1)
        
        # Sort by RSSI (strongest first) and extract only SSIDs
        return [ssid for ssid, _ in sorted(set(networks), key=lambda x: x[1], reverse=True)] 