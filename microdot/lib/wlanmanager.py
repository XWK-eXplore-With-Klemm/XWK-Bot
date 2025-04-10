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

class WlanManagerUi:
    """Base UI handler interface for WlanManager"""
    
    # Connection status
    def on_connect_no_wifi_config_found(self): pass
    def on_connect_start(self, ssid): pass
    def on_connect_progress(self): pass
    def on_connect_success(self, ip, mac): pass
    def on_connect_timeout(self): pass
    def on_connect_aborted(self): pass
    def on_connect_failed(self): pass
    def on_connect_error(self, error): pass
    
    # AP mode status
    def on_ap_start(self, ap_ssid, ip): pass
    def on_config_saved(self, ssid): pass
    
    # Network scanning
    def on_scan_start(self): pass
    def on_scan_complete(self, networks): pass
    
    # Input/Control methods
    def should_abort_connection(self) -> bool:
        """Check if connection attempt should be aborted"""
        return False
    
    def get_connection_timeout(self) -> int:
        """Get connection timeout in seconds"""
        return 30

class WlanManager:
    def __init__(self, microdot, ui=None, project_name="MICRODOT", config=None):
        """
        Initialize WiFi manager
        :param microdot: Microdot instance to add routes to
        :param ui: Optional WlanManagerUi instance for UI interactions
        :param project_name: Name used for AP SSID (default: MICRODOT)
        :param config: Optional Iniconf instance for configuration (creates new one if None)
        """
        self.microdot = microdot
        self.ui = ui or WlanManagerUi()
        self.project_name = project_name
        self.config = config or Iniconf()

    def connect(self):
        """
        Try to connect to configured WiFi network
        Returns True if connected, False if connection failed
        """
        gc.collect()
        print("Memory before WiFi:", gc.mem_free())
        
        ssid = self.config.get('WLAN_SSID')
        password = self.config.get('WLAN_PASSWORD')
        
        if not ssid or not password:
            print("No valid WiFi configuration found")
            self.ui.on_connect_no_wifi_config_found()
            return False

        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            if not wlan.isconnected():
                print(f"Connecting to WiFi: {ssid}")
                self.ui.on_connect_start(ssid)
                wlan.connect(ssid, password)

                start_time = time.time()
                while not wlan.isconnected() and time.time() - start_time < self.ui.get_connection_timeout():
                    if self.ui.should_abort_connection():
                        wlan.disconnect()
                        self.ui.on_connect_aborted()
                        return False
                    self.ui.on_connect_progress()
                    time.sleep(0.2)

                if not wlan.isconnected():
                    self.ui.on_connect_timeout()
                    return False

            if wlan.isconnected():
                print("Successfully connected to WiFi")
                mac = ubinascii.hexlify(wlan.config('mac')).decode().upper()
                mac = ":".join([mac[i:i+2] for i in range(0, len(mac), 2)])
                ip = wlan.ifconfig()[0]
                print(f"IP: {ip}")
                self.ui.on_connect_success(ip, mac)
                gc.collect()
                print("Memory after WiFi connection:", gc.mem_free())
                return True
                
            print("Could not connect to WiFi")
            self.ui.on_connect_failed()
            return False
            
        except Exception as e:
            print("WiFi connection error:", e)
            self.ui.on_connect_error(e)
            return False

    def start_ap(self):
        """Start access point mode with configuration portal"""
        # Only import heavy dependencies when AP mode is actually needed
        import machine
        from microdot import Response
        from lib.phew import dns
        
        # Register routes for the captive portal
        self._register_routes()
        
        print("Starting AP mode")
        self.ui.on_scan_start()  # Add UI notification
        
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
        
        self.ui.on_ap_start(ap_ssid, ip)  # Add UI notification
        
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
            import asyncio
            
            form = request.form
            ssid = form.get('ssid')
            password = form.get('password')
            
            if ssid and password:
                print(f"Saving WiFi configuration: {ssid}")
                try:
                    self.config.set('WLAN_SSID', ssid)
                    self.config.set('WLAN_PASSWORD', password)
                    self.config.save()
                    self.ui.on_config_saved(ssid)
                    
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