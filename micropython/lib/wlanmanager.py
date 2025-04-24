"""
WiFi configuration manager with web configuration portal
"""

import gc
import network
import time
import machine
import ubinascii
import json
from iniconf import Iniconf
from microWebSrv import MicroWebSrv
from lib.phew import dns

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
    def __init__(self, ui=None, project_name="MY-PROJECT", config=None):
        """
        Initialize WiFi manager
        :param ui: Optional WlanManagerUi instance for UI interactions
        :param project_name: Name used for AP SSID (default: MY-PROJECT)
        :param config: Optional Iniconf instance for configuration (creates new one if None)
        """
        self.ui = ui or WlanManagerUi()
        self.project_name = project_name
        self.config = config or Iniconf(debug=True)
        self.web_server = None
        self._cached_networks = None  # Cache for network scan results

    def connect(self):
        """
        Try to connect to configured WiFi network
        Returns True if connected, False if connection failed
        """
        gc.collect()
        print("Memory before WiFi:", gc.mem_free())
        
        # wlan.connect() expects strings e.g. for config value 1234
        ssid = str(self.config.get('WLAN_SSID'))
        password = str(self.config.get('WLAN_PASSWORD'))
        
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
        gc.collect()
        print("Memory at start of AP mode:", gc.mem_free())
        
        # Start AP mode
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(0.1)
        ap.active(True)
        
        # Get last 4 characters of MAC address
        sta_if = network.WLAN(network.STA_IF)
        mac = ubinascii.hexlify(sta_if.config('mac')).decode()
        ap_ssid = f"{self.project_name}-{mac[-4:].upper()}"
        
        ap.config(essid=ap_ssid,
                 authmode=network.AUTH_OPEN,
                 channel=1,
                 hidden=False)
        
        # Get AP IP and notify UI before loading web dependencies
        ip = ap.ifconfig()[0]
        self.ui.on_ap_start(ap_ssid, ip)
        
        print("Access Point active!")
        print(f"SSID: {ap_ssid}")
        print(f"IP: {ip}")

        gc.collect()
        print("Memory after AP:", gc.mem_free())

        try:
            print("Starting DNS server for captive portal...")
            dns.run_catchall(ip)

            gc.collect()
            print("Memory after DNS:", gc.mem_free())
            
            # Setup route handlers
            route_handlers = [
                # Main config routes
                ('/wifi-config', 'GET', self._handle_wifi_config),
                ('/wifi-config', 'POST', self._handle_wifi_config_post)
            ]
            
            # Set up captive portal redirects for common URLs
            captive_portal_urls = [
                '/',  # Root path
                '/generate_204',  # Android
                '/hotspot-detect.html',  # Apple
                '/connecttest.txt',  # Windows
                '/ncsi.txt',  # Windows
                '/fwlink/',  # Microsoft
                '/redirect'  # Common redirect
            ]
            
            # Create route handlers for captive portal URLs
            def handle_captive_redirect(client, response):
                response.WriteResponseRedirect(f'http://{ip}/wifi-config')
            
            # Combine main routes with captive portal routes
            all_routes = route_handlers + [(url, 'GET', handle_captive_redirect) for url in captive_portal_urls]
            
            # Create web server with all routes
            self.web_server = MicroWebSrv(routeHandlers=all_routes, port=80)
            
            # Remove the catch-all redirect
            # self.web_server.SetNotFoundPageUrl(f'http://{ip}/wifi-config')
            
            self.web_server.Start(threaded=True)

            gc.collect()
            print("Memory after web server start:", gc.mem_free())

            # Start event loop to keep DNS server running
            print("Starting event loop for DNS server...")
            import uasyncio
            try:
                loop = uasyncio.get_event_loop()
                loop.run_forever()
            except Exception as e:
                print(f"Error in event loop: {e}")
            finally:
                print("Event loop stopped")
            
            return True
            
        except Exception as e:
            print("Error starting web services:", e)
            return False

    def _handle_wifi_config(self, client, response):
        """Serve WiFi configuration page"""
        networks = self._scan_networks()
        with open('templates/wlanmanager_config.html', 'r') as f:
            content = f.read()
            # Simple template replacement
            content = content.replace('{{ project_name }}', self.project_name)
            content = content.replace('{{ networks }}', json.dumps(networks))
        response.WriteResponseOk(contentType="text/html", content=content)

        gc.collect()
        print("Memory after wifi config GET request:", gc.mem_free())

    def _handle_wifi_config_post(self, client, response):
        """Handle WiFi configuration form submission"""
        form_data = client.ReadRequestPostedFormData()
        ssid = form_data.get('ssid')
        password = form_data.get('password')
        # decode URL-encoded spaces 
        ssid = ssid.replace('+', ' ')
        password = password.replace('+', ' ')
        print(f"Decoded SSID: {ssid}")
        print(f"Decoded Password: {password}")
        
        if ssid and password:
            print(f"Saving WiFi configuration: {ssid}")
            try:
                # Decode URL-encoded SSID and password before saving    
                self.config.set('WLAN_SSID', ssid)
                self.config.set('WLAN_PASSWORD', password)
                print("Config set ssid and password")
                self.config.save()
                print("Config saved successfully")

                
                gc.collect()
                print("Memory after config save:", gc.mem_free())
                # Somehow this fails... (server error, recursion limit exceed`?)
                #self.ui.on_config_saved(ssid)
                
                
                with open('templates/wlanmanager_success.html', 'r') as f:
                    content = f.read()
                response.WriteResponseOk(contentType="text/html", content=content)

                gc.collect()
                print("Memory after html response:", gc.mem_free())
                
                # Schedule reset
                #import machine
                #machine.Timer(-1).init(period=2000, mode=machine.Timer.ONE_SHOT, callback=lambda #t:machine.reset())

                print("Resetting...")
                time.sleep(2)
                machine.reset()
                
            except Exception as e:
                print(f"Error saving config: {e}")
                with open('templates/wlanmanager_error.html', 'r') as f:
                    content = f.read().replace('{{ error }}', str(e))
                response.WriteResponseOk(contentType="text/html", content=content)
        else:
            response.WriteResponseRedirect('/wifi-config')

    def _scan_networks(self):
        """Scan for available WiFi networks and sort by signal strength"""
        """Cache results to avoid scanning every time for multiple requests"""
        # Return cached results if available
        if self._cached_networks is not None:
            return self._cached_networks

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
        final_networks = [ssid for ssid, _ in sorted(set(networks), key=lambda x: x[1], reverse=True)]
        print(final_networks)

        # Cache the results
        self._cached_networks = final_networks

        gc.collect()
        print("Memory after WiFi scan:", gc.mem_free())
        
        return final_networks
