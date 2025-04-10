"""Bot-specific UI implementation for WlanManager"""

from machine import Pin
from microdot.lib.wlanmanager import WlanManagerUi

class WlanManagerUiBot(WlanManagerUi):
    def __init__(self, write_fn, button_a_pin):
        """
        Initialize Bot UI handler
        :param write_fn: Function to write text to display
        :param button_a_pin: Pin object for abort button
        """
        self.write = write_fn
        self.button_a = button_a_pin
        # Define colors as RGB tuples (0-255 for each component)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.CYAN = (0, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.GREY = (128, 128, 128)
    
    def on_scan_start(self):
        self.write("Scanning for WiFis...", color=self.GREY)
    
    def on_scan_complete(self, networks):
        pass  # We don't show network list on the display to save space
    
    def on_connect_start(self, ssid):
        self.write("Connecting to WiFi", color=self.WHITE)
        self.write(f"{ssid}", color=self.CYAN)
        self.write("Press A to abort", color=self.GREY)
    
    def on_connect_progress(self):
        pass  # Could add animation here if desired
    
    def on_connect_success(self, ip, mac):
        self.write("Success!", color=self.GREEN)
        self.write(f"MAC: {mac}", color=self.GREY)
        self.write("")  # Newline
        self.write("Open in your webbrowser:", color=self.WHITE)
        self.write(f"http://{ip}", color=self.CYAN)
    
    def on_connect_failure(self, error):
        self.write(error, color=self.YELLOW)
    
    def on_ap_start(self, ap_ssid, ip):
        self.write("Access Point active!", color=self.GREEN)
        self.write("Please connect to WiFi:")
        self.write(f"{ap_ssid}", color=self.CYAN)
        self.write("")
        self.write("Then open in webbrowser:", color=self.WHITE)
        self.write(f"http://{ip}", color=self.CYAN)
        self.write("and configure your WiFi")
    
    def on_config_saved(self, ssid):
        self.write(f"Saving WiFi configuration: {ssid}", color=self.GREY)
    
    def should_abort_connection(self) -> bool:
        """Check if button A is pressed to abort"""
        return not self.button_a.value()  # Button is pulled up, so pressed = False
    
    def get_connection_timeout(self) -> int:
        """Get connection timeout in seconds"""
        return 30  # Use default timeout 