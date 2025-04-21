"""
Pixel Painter Library
Common functions for LED matrix manipulation and control
"""

from machine import Pin, ADC, PWM
import neopixel
import time
import ujson
import random
import ubinascii
from font_3x5 import FONT_3X5

### CONSTANTS
LED_PIN = 16            # The pin where the LED matrix is connected
NUM_LEDS = 64          # Number of total leds in the matrix
MATRIX_WIDTH = 8        # Width of the matrix ("x")
MATRIX_HEIGHT = 8       # Height of the matrix ("y")

BRIGHTNESS_PIN = 32     # Brightness potentiometer
BRIGHTNESS_MAX = 100    # Maximum brightness to stay below 500mA current consumption

# Button pin definitions
BUTTON_UP_PIN = 23
BUTTON_RIGHT_PIN = 22
BUTTON_DOWN_PIN = 21
BUTTON_LEFT_PIN = 19
BUTTON_Y_PIN = 4
BUTTON_X_PIN = 0
BUTTON_B_PIN = 2
BUTTON_A_PIN = 15

# Initialize hardware
leds = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)
brightness_pot = ADC(Pin(BRIGHTNESS_PIN))
brightness_pot.width(ADC.WIDTH_10BIT)
brightness_pot.atten(ADC.ATTN_11DB)
beeper = PWM(Pin(17))
beeper.duty(0)  # Ensure beeper is silent at startup

# Initialize button pins
Pin(BUTTON_UP_PIN, Pin.IN, Pin.PULL_UP) 
Pin(BUTTON_RIGHT_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_DOWN_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_LEFT_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_Y_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_X_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)

def xy(x, y):
    """Map 2D coordinates to 1D index"""
    return y * MATRIX_WIDTH + x

def beep(frequency=1000, duration_ms=250):
    """Generate a beep sound"""
    beeper.freq(frequency)
    beeper.duty(512)
    time.sleep_ms(duration_ms)
    beeper.duty(0)
    
def shutup():
    """Stop the beeper"""
    beeper.duty(0)

def set_matrix_brightness():
    """Set brightness level of LED matrix (0-255)"""
    brightness = int(brightness_pot.read() / 1023 * BRIGHTNESS_MAX)
    brightness = 1 if brightness == 0 else brightness
    
    for i in range(NUM_LEDS):
        leds[i] = tuple(int(c * brightness / 255) for c in leds[i])

def write_leds():
    """Output leds to the matrix with current brightness"""
    set_matrix_brightness()
    leds.write()

def show_picture(picture):
    """Display a picture on the LED matrix"""
    for i in range(NUM_LEDS):
        leds[i] = picture[i]
    write_leds()

def load_from_file(filename="picture.json", target=None):
    """Load LED data from a JSON file"""
    try:
        with open(filename, "r") as file:
            loaded_data = ujson.load(file)
            if target is None:
                target = [(0, 0, 0)] * NUM_LEDS
            for i in range(min(NUM_LEDS, len(loaded_data))):
                target[i] = tuple(loaded_data[i])
            return target
    except OSError:
        print("File does not exist or cannot be read")
        return None

def save_to_file(data, filename="picture.json"):
    """Save LED data to a JSON file"""
    try:
        with open(filename, "w") as file:
            ujson.dump([list(color) for color in data], file)
    except:
        print("Error saving file")

def blend(source, target, steps=30):
    """Animated blending between two color states"""
    # Get source data
    if isinstance(source, tuple):
        source_data = [source] * NUM_LEDS
    elif isinstance(source, str) and source == "leds":
        source_data = [leds[i] for i in range(NUM_LEDS)]
    else:
        source_data = source

    # Get target data
    if isinstance(target, tuple):
        target_data = [target] * NUM_LEDS
    elif isinstance(target, str) and target == "leds":
        target_data = [leds[i] for i in range(NUM_LEDS)]
    else:
        target_data = target

    # Calculate and apply increments
    step_increments = []
    for i in range(NUM_LEDS):
        r1, g1, b1 = source_data[i]
        r2, g2, b2 = target_data[i]
        
        r_inc = (r2 - r1) / steps
        g_inc = (g2 - g1) / steps
        b_inc = (b2 - b1) / steps
        
        step_increments.append((r_inc, g_inc, b_inc))

    for step in range(steps):
        for i in range(NUM_LEDS):
            r_current, g_current, b_current = source_data[i]
            r_increment, g_increment, b_increment = step_increments[i]
            
            r_next = int(r_current + r_increment)
            g_next = int(g_current + g_increment)
            b_next = int(b_current + b_increment)
            
            r_next = max(0, min(255, r_next))
            g_next = max(0, min(255, g_next))
            b_next = max(0, min(255, b_next))
            
            new_color = (r_next, g_next, b_next)
            source_data[i] = new_color
            leds[i] = new_color

        write_leds()

def fill(color):
    """Fill the entire LED matrix with a single color"""
    # Special case for black - direct write without brightness adjustment
    if color == (0, 0, 0):
        for i in range(NUM_LEDS):
            leds[i] = color
        leds.write()
    else:
        for i in range(NUM_LEDS):
            leds[i] = color
        write_leds()

def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB color"""
    if s == 0:
        return (v, v, v)
        
    region = h // 43
    remainder = (h - (region * 43)) * 6
    
    p = (v * (255 - s)) // 255
    q = (v * (255 - ((s * remainder) // 255))) // 255
    t = (v * (255 - ((s * (255 - remainder)) // 255))) // 255
    
    if region == 0:
        return (v, t, p)
    elif region == 1:
        return (q, v, p)
    elif region == 2:
        return (p, v, t)
    elif region == 3:
        return (p, q, v)
    elif region == 4:
        return (t, p, v)
    else:
        return (v, p, q) 

def xwk_intro():
    """Display the XWK intro animation"""
    picture = load_from_file("xwk.json")
    blend((0, 0, 0), picture, 10)
    time.sleep(0.2)
    blend(picture, (0, 0, 0), 10)
    fill((0, 0, 0))
    time.sleep(0.2) 

def start_ap_mode():
    """Start access point mode with configuration portal"""
    import network
    from microWebSrv import MicroWebSrv
    
    # First scan for networks
    print("\nScanning for WiFi networks...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)  # First deactivate
    time.sleep(0.1)      # Wait a bit
    sta_if.active(True)  # Then reactivate
    time.sleep(2)        # Give WiFi time to initialize
    
    networks = []
    for _ in range(3):  # Try scanning up to 3 times
        scan_result = sta_if.scan()
        # Filter out empty SSIDs and convert bytes to string
        networks = [net for net in scan_result if net[0] and len(net[0].strip()) > 0]
        if networks:
            break
        print("No networks found, retrying...")
        time.sleep(1)
    
    networks.sort(key=lambda x: x[3], reverse=True)  # Sort by signal strength
    
    print("\nAvailable networks:")
    print("------------------")
    for net in networks:
        ssid = net[0].decode('utf-8')
        bssid = ":".join(["{:02x}".format(b) for b in net[1]])
        channel = net[2]
        rssi = net[3]
        security = "🔒" if net[4] > 0 else "🔓"
        print(f"{security} {ssid:20} Ch:{channel:2d} RSSI:{rssi:3d}dB MAC:{bssid}")
    print("------------------\n")
    
    # Then start AP
    ap = network.WLAN(network.AP_IF)
    ap.active(False)  # First deactivate
    time.sleep(0.1)   # Wait a bit
    ap.active(True)   # Then reactivate
    
    # Get last 4 characters of MAC address
    mac = ubinascii.hexlify(sta_if.config('mac')).decode()
    ap_ssid = f"PIX_{mac[-4:].upper()}"
    
    # Configure the access point with more permissive settings
    ap.config(essid=ap_ssid,
             authmode=network.AUTH_OPEN,
             channel=1,            # Use channel 1
             hidden=False)         # Make sure it's not hidden

    print('Access Point active')
    print('SSID:', ap_ssid)
    print('IP:', ap.ifconfig()[0])

    # Show AP mode status on LED matrix with scrolling text in a loop. Do this in a separate thread to not block the webserver
    def scroll_loop():
        while True:
            scroll_text(f"USE WIFI {ap_ssid}", color=(0, 0, 255), speed=0.1)
            time.sleep(0.1)  # Small delay between repetitions

    import _thread
    _thread.start_new_thread(scroll_loop, ())

    # Web server route handlers
    def _httpHandlerConfig(httpClient, httpResponse):
        # Create network options HTML
        network_options = ""
        for net in networks:
            ssid = net[0].decode('utf-8')
            network_options += f'<option value="{ssid}">{ssid}</option>'

        # Note: this markup easily runs into a size limit, so we need to keep it short
        content = f"""
        <html><head>
            <title>XWK WiFi Setup</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                select, input {{ margin: 10px 0; padding: 5px; width: 200px; }}
                form {{ max-width: 300px; margin: 0 auto; }}
            </style>
        </head><body>
            <h1>XWK WiFi Setup</h1>
            <form method="POST" action="/">
                <select name="ssid" required>
                    <option value="">Select Network...</option>
                    {network_options}
                </select><br>
                <input type="text" name="password" placeholder="Password" required><br>
                <input type="submit" value="Connect">
            </form>
        </body></html>
        """
        httpResponse.WriteResponseOk(headers=None,
                                  contentType="text/html",
                                  contentCharset="UTF-8",
                                  content=content)

    def _httpHandlerConfigPost(httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()
        ssid = formData["ssid"]
        password = formData["password"]
        
        print(f"\nSaving configuration for network: {ssid}")
        
        # Save to config.json
        with open('config.json', 'w') as f:
            ujson.dump({'wlan_ssid': ssid, 'wlan_password': password}, f)
        
        content = """
        <html><head>
            <title>Configuration Saved</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; text-align: center; }
            </style>
        </head><body>
            <h1>Configuration Saved!</h1>
            <p>The device will now restart and try to connect to the selected network.</p>
        </body></html>
        """
        
        # Send response with Connection: close header
        httpResponse.WriteResponseOk(
            headers = {
                "Connection": "close",
                "Cache-Control": "no-store"
            },
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
        )
        
        # Give browser time to render the response
        time.sleep(2)
        
        # Schedule restart
        def _restart():
            time.sleep(1)
            import machine
            machine.reset()
        import _thread
        _thread.start_new_thread(_restart, ())

    # Create and start web server
    srv = MicroWebSrv(routeHandlers=[
        ( "/", "GET", _httpHandlerConfig ),
        ( "/", "POST", _httpHandlerConfigPost )
    ])
    
    # Set not found URL to redirect to config page
    srv.SetNotFoundPageUrl("/")
    
    # Start server
    srv.Start(threaded=False)

    # Keep server running
    while True:
        time.sleep(1)

def network_setup():
    """Setup network connection using config.json"""
    print("Activating network")
    import network
    import time
    import ubinascii

    # Try to load configuration
    try:
        with open('config.json', 'r') as f:
            config = ujson.load(f)
    except (OSError, ValueError) as e:
        print("No valid config.json found - starting AP mode")
        start_ap_mode()
        return False

    try:
        wlan = network.WLAN(network.STA_IF)
        if not wlan.active():
            wlan.active(True)
            time.sleep(0.1)  # Give WiFi some time to initialize
        
        if not wlan.isconnected():
            print(f"Connecting to {config['wlan_ssid']}...")
            wlan.connect(config['wlan_ssid'], config['wlan_password'])

            # Try to connect to WLAN for 5 seconds
            start_time = time.time()
            dots = 0
            while not wlan.isconnected() and time.time() - start_time < 15:
                # Show loading animation
                if dots < NUM_LEDS:
                    leds[dots] = (50, 50, 50)  # Grey
                    write_leds()
                    dots += 1
                time.sleep(0.5)

            # Clear the loading animation
            fill((0, 0, 0))

        if wlan.isconnected():
            mac = ubinascii.hexlify(wlan.config('mac')).decode().upper()
            mac = ":".join([mac[i:i+2] for i in range(0, len(mac), 2)])
            ip_address = wlan.ifconfig()[0]
            print(f'WLAN: {config["wlan_ssid"]}')
            print(f'MAC:  {mac}')
            print(f'IP:   {ip_address}')
            
            # Display IP address in green
            scroll_text(ip_address, color=(0, 255, 0), speed=0.1)
            
            print("\nStarting webrepl")
            try:
                import webrepl
                webrepl.start()
            except Exception as e:
                print("WebREPL error:", e)
            
            print("Starting IDE web service")
            try:
                import weditor.start
            except Exception as e:
                print("Web editor error:", e)
            
            return True
        else:
            print("WiFi connection failed - starting AP mode")
            start_ap_mode()
            return False
            
    except Exception as e:
        print("WiFi setup error:", e)
        start_ap_mode()
        return False

def render_char(char, x_offset=0, color=(255, 255, 255)):
    """Render a single character from the 3x5 font at the specified x offset"""
    if char.upper() not in FONT_3X5:
        return
    
    char_data = FONT_3X5[char.upper()]
    for y in range(5):  # Height of font
        row = char_data[y]
        for x in range(3):  # Width of font
            if row & (1 << (2-x)):  # Check each bit
                pixel_x = x + x_offset
                pixel_y = y + 1  # Center vertically with 1 pixel padding
                if 0 <= pixel_x < MATRIX_WIDTH and 0 <= pixel_y < MATRIX_HEIGHT:
                    leds[xy(pixel_x, pixel_y)] = color

def scroll_text(text, color=(255, 255, 255), speed=0.03):
    """Scroll text across the display from right to left"""
    # Convert text to uppercase since our font only has uppercase
    text = text.upper()
    
    # Pre-calculate brightness-adjusted color
    # We do this for speed reasons
    brightness = int(brightness_pot.read() / 1023 * BRIGHTNESS_MAX)
    brightness = 1 if brightness == 0 else brightness
    adjusted_color = tuple(int(c * brightness / 255) for c in color)
    
    # Calculate total width of text (3 pixels per char + 1 pixel spacing)
    total_width = len(text) * 4 - 1
    
    # Fill with black once at the start
    fill((0, 0, 0))
    
    # Start from the right edge of the display
    for pos in range(MATRIX_WIDTH, -total_width - 1, -1):
        # Reset all pixels that might have been set in previous frame
        fill((0, 0, 0))
        
        # Render each character
        for i, char in enumerate(text):
            char_pos = pos + (i * 4)  # 4 pixels per character (3 + 1 space)
            if -3 <= char_pos <= MATRIX_WIDTH:
                render_char(char, char_pos, adjusted_color)
        
        # Write directly without brightness adjustment
        leds.write()
        time.sleep(speed)

def display_text(text, color=(255, 255, 255)):
    """Display static text centered on the display"""
    # Convert text to uppercase
    text = text.upper()
    
    # Calculate total width
    text_width = len(text) * 4 - 1
    
    # Calculate starting position to center the text
    start_x = (MATRIX_WIDTH - text_width) // 2
    
    # Clear display
    fill((0, 0, 0))
    
    # Render each character
    for i, char in enumerate(text):
        char_pos = start_x + (i * 4)
        render_char(char, char_pos, color)
    
    write_leds() 
