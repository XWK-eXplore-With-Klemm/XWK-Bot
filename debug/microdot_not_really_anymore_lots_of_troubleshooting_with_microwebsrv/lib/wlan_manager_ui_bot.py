"""XWK-Bot-specific UI implementation for WlanManager"""

from lib.wlanmanager import WlanManagerUi
import bot

class WlanManagerUiBot(WlanManagerUi):
    def on_scan_start(self):
        bot.write("Scanning for WiFis...", color=bot.GREY)
    
    def on_scan_complete(self, networks):
        if not networks:
            bot.write("No networks found, retrying...", color=bot.YELLOW)
    
    def on_connect_start(self, ssid):
        bot.write("Connecting to WiFi", color=bot.WHITE)
        bot.write(f"{ssid}", color=bot.CYAN)
        bot.write("Press A to abort", color=bot.GREY)
    
    def on_connect_progress(self):
        pass  # Original code had animation commented out
    
    def on_connect_success(self, ip, mac):
        bot.write("Success!", color=bot.GREEN)
        bot.write(f"MAC: {mac}", color=bot.GREY)
        bot.write("")  # Newline
        bot.write("Open in your webbrowser:", color=bot.WHITE)
        bot.write(f"http://{ip}", color=bot.CYAN)
    
    def on_connect_no_wifi_config_found(self):
        bot.write("No WiFi config", color=bot.YELLOW)
    
    def on_connect_timeout(self):
        bot.write("WiFi not connected", color=bot.YELLOW)
        bot.write("Starting AP mode")
        bot.sleep(1)
    
    def on_connect_aborted(self):
        pass  # Original code just breaks the loop
    
    def on_connect_failed(self):
        bot.write("WiFi not connected", color=bot.YELLOW)
        bot.write("Starting AP mode")
        bot.sleep(1)
    
    def on_connect_error(self, error):
        bot.write(f"WiFi error: {error}", color=bot.YELLOW)
    
    def on_ap_start(self, ap_ssid, ip):
        bot.reset_terminal()
        bot.write("Access Point active!", color=bot.GREEN)
        bot.write("Please connect to Wifi:")
        bot.write(f"{ap_ssid}", color=bot.CYAN)
        bot.write("")
        bot.write("Then open in webbrowser:", color=bot.WHITE)
        bot.write(f"http://{ip}", color=bot.CYAN)
        bot.write("and configure your WiFi")
    
    def on_config_saved(self, ssid):
        bot.write(f"Saving WiFi configuration: {ssid}", color=bot.GREY)
    
    def should_abort_connection(self) -> bool:
        """Check if button A is pressed to abort"""
        return bot.is_pressed(bot.BUTTON_A)
    
    def get_connection_timeout(self) -> int:
        """Get connection timeout in seconds"""
        return 30 