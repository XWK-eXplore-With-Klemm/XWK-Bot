import gc
import machine
from machine import Pin, SPI, ADC, PWM
import time
import network
import ubinascii
from ST7735 import TFT, TFTColor # GMT-177-01 128x160px TFTST7735 display
from sysfont import sysfont
import hcsr04 # ultra sound HC-SR04 sensor
import os
from ini_parser import IniParser

### CONFIG HANDLING
# Make sure we use absolute path for config file
CONFIG_FILE = '/config.ini'  # Root directory of the filesystem
_config_parser = IniParser()
CONFIG_FILE_CONTENT_CACHE = None

def config_get(key, default=None):
    """Get a config value by key"""
    try:
        global CONFIG_FILE_CONTENT_CACHE
        
        # Load config file if not cached
        try:
            if CONFIG_FILE_CONTENT_CACHE is None:
                type="from file"
                with open(CONFIG_FILE, 'r') as f:
                    CONFIG_FILE_CONTENT_CACHE = f.read()
                    _config_parser.loads(CONFIG_FILE_CONTENT_CACHE)
            else:
                type="from cache"
                _config_parser.loads(CONFIG_FILE_CONTENT_CACHE)
                
            value = _config_parser.get(key, default)    
            #print("config_get()", CONFIG_FILE, type, key, value)
                
            return value
            
        except Exception as e:
            print("Error loading config", CONFIG_FILE, key, e)
            return default
            
    except Exception as e:
        print("config_get() error", CONFIG_FILE, key, e)
        return default

def config_set(key, value):
    """Set a config value by key"""
    try:
        # Load existing config or create new
        try:
            with open(CONFIG_FILE, 'r') as f:
                _config_parser.loads(f.read())
        except Exception as e:
            print("No config file found, creating new one", CONFIG_FILE, key, value, e)
            
        # Set the value
        _config_parser.set(key, str(value))
        
        # Save back to file
        with open(CONFIG_FILE, 'w') as f:
            f.write(_config_parser.dumps())
            #print("config_set()", CONFIG_FILE, key, value)
            
        # Update cache after successful save
        global CONFIG_FILE_CONTENT_CACHE
        CONFIG_FILE_CONTENT_CACHE = _config_parser.dumps()
            
        return True
    except Exception as e:
        print("config_set() error", CONFIG_FILE, key, value, e)
        return False

### DISPLAY
# Load display pin configuration
SCK_PIN = config_get('SCK_PIN')
SDA_PIN = config_get('SDA_PIN')
DC_PIN = config_get('DC_PIN')
RESET_PIN = config_get('RESET_PIN')
CS_PIN = config_get('CS_PIN')

spi = SPI(1, baudrate=60000000, polarity=0, phase=0, miso=None) # Using default SPI pins from >>> print(machine.SPI(1))

def rgb_to_tft_color(rgb_tuple):
    """Convert RGB tuple (0-255 per channel) to 16-bit RGB565 format
    
    Args:
        rgb_tuple: Tuple of (r,g,b) values from 0-255
        
    Returns:
        16-bit RGB565 color value
    """
    r, g, b = rgb_tuple
    return TFTColor(r, g, b)

# Define colors as RGB tuples (0-255 for each component)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
GRAY = (128, 128, 128)

# Initialize display
tft=TFT(spi, DC_PIN, RESET_PIN, CS_PIN)
tft.initr()
tft.rgb(True)
tft.rotation(1) # landscape orientation - pins on the right
tft.fill(rgb_to_tft_color(BLACK)) # reset screen to black

# "Terminal", write to next line until display is full, then reset
#def write(text, color = TFT.WHITE):
#    tft.terminal(text, color, sysfont)
def write(*args, **kwargs):    
    text = ""
    
    # Convert normal arguments to string and concatenate
    for arg in args:        
        text += str(arg)
        
    # Check for keyword arguments
    color = WHITE  # Now using our RGB tuple colors
    newline = True
    line = None
    
    if 'color' in kwargs:
        color = kwargs['color']
    if 'newline' in kwargs:
        newline = kwargs['newline']
    if 'line' in kwargs:
        line = kwargs['line']
        newline = False  # Force newline to False when using line parameter

    # Convert RGB tuple to TFT color
    tft_color = rgb_to_tft_color(color)
        
    tft.terminal(text, tft_color, sysfont, newline, line)

def reset_terminal():
    """Reset the terminal cursor position to top of screen"""
    tft.terminal_reset()  # Use TFT's terminal reset function

### ULTRASONIC
# Load ultrasonic pin configuration
TRIGGER_PIN = config_get('TRIGGER_PIN')
ECHO_PIN = config_get('ECHO_PIN')

trigger_pin = machine.Pin(TRIGGER_PIN)
echo_pin = machine.Pin(ECHO_PIN)
uss = hcsr04.HCSR04(trigger_pin, echo_pin)

def distance():
    try:
        distance = uss.distance_cm()
        return int(distance)
    except Exception as e:
        print("Error measuring distance:", e)
        return None    


### LDR
# Connect LDR (Light dependent resistor) to 3.3V and via a 2K resistor to ground
# Connect the junction between LDR and 2K resistor to a GPIO
# Gives values between 0 and 4095. Room light level ~ 2000
#ldrA = ADC(Pin(33))  # Replace with the ADC pin number you are using
#ldrA.atten(ADC.ATTN_11DB)  # Set attenuation for full range of ADC
#ldrB = ADC(Pin(32))  # Replace with the ADC pin number you are using
#ldrB.atten(ADC.ATTN_11DB)  # Set attenuation for full range of ADC

#def brightness(ldr):
#    if ldr == 'A' or ldr == 'L':
#        return ldrA.read()
#    elif ldr == 'B' or ldr == 'R':
#        return ldrB.read()
#    
#    return 0

### BATTERY

def battery_voltage_read():
    # Create ADC object on the VBAT pin
    # Note: You'll need to identify the correct pin number from your board's pinout
    adc = ADC(Pin(35))  # This pin number may need to be adjusted for your specific board
    
    # Configure ADC
    adc.atten(ADC.ATTN_11DB)  # Full range: 3.3V
    adc.width(ADC.WIDTH_12BIT)  # 12-bit resolution
    
    # Read raw value
    raw_value = adc.read()
    
    # Convert to voltage
    # With 12-bit resolution (0-4095) and 3.3V reference
    voltage = (raw_value * 3.3) / 4095.0

    # Add calibration factor (displayed voltage vs multimeter measurement)
    calibration_factor = 1.015
    
    # If there's a voltage divider on your board, adjust the calculation
    # Example: if it's a 1:2 divider, multiply by 2
    actual_voltage = voltage * 2 * calibration_factor 
    
    return actual_voltage

def battery_voltage_warning():
    # For 4*1.5V AAA batteries
    voltage = battery_voltage_read()

    if voltage > 5.2:   
        return False
    
    if voltage < 4.7:
        write(f"Battery empty! {voltage:.2f}V", color=RED)
        rgb_led(RED)
    else:
        write(f"Battery soon empty! {voltage:.2f}V", color=YELLOW)
        rgb_led(YELLOW)

    beep(1000, 100)
    sleep(0.1)
    beep(1000, 100)
    sleep(0.1)
    beep(1000, 100)        

    sleep(1)

    rgb_led(BLACK)
    reset_terminal()

### MOTOR BOARD MX1508
# Connect all ground / minus pins (battery, motor controller, microcontroller
# Connect plus of motor controller to battery plus

# Motor alignment adjustment (-100 to +100)
# Negative values slow down left motor
# Positive values slow down right motor
MOTOR_ALIGNMENT = config_get('MOTOR_ALIGNMENT', default=0)

# Motor A Control Pins
# Do not use pins 15,2,0,4 -> 15 and 0 are 3.3V at boot!
MOTOR_LEFT_FORWARD_PIN = config_get('LEFT_FORWARD_PIN')
MOTOR_LEFT_BACKWARD_PIN = config_get('LEFT_BACKWARD_PIN')
MOTOR_RIGHT_FORWARD_PIN = config_get('RIGHT_FORWARD_PIN')
MOTOR_RIGHT_BACKWARD_PIN = config_get('RIGHT_BACKWARD_PIN')

# Initialize motor PWM pins
INT1_A = PWM(Pin(MOTOR_LEFT_FORWARD_PIN))
INT2_A = PWM(Pin(MOTOR_LEFT_BACKWARD_PIN))
INT1_B = PWM(Pin(MOTOR_RIGHT_FORWARD_PIN))
INT2_B = PWM(Pin(MOTOR_RIGHT_BACKWARD_PIN))

MOTOR_PWM_FREQUENCY = 500

# Initialize PWM
INT1_A.freq(MOTOR_PWM_FREQUENCY)  
INT2_A.freq(MOTOR_PWM_FREQUENCY)
INT1_B.freq(MOTOR_PWM_FREQUENCY)
INT2_B.freq(MOTOR_PWM_FREQUENCY)

# Motor control constants
MIN_SPEED = 0  # Minimum speed that reliably moves the motors
MIN_DURATION_MS = 80  # Minimum duration of normal speed motor movement in milliseconds
KICK_START_SPEED = 70  # Speed for initial kick
KICK_START_DURATION_MS = 20  # Duration of kick in milliseconds

def motor_alignment(speed=15):
    """Interactive calibration of motor alignment
    Use LEFT/RIGHT buttons to adjust if robot veers to one side
    Press A to save and exit
    
    Negative values slow down left motor
    Positive values slow down right motor"""
    global MOTOR_ALIGNMENT
    
    reset_terminal()
    write("Motor Alignment", color=CYAN)
    write("Press LEFT/RIGHT to adjust", color=WHITE)
    write("LEFT = more to the left", color=GREY)
    write("RIGHT = more to the right", color=GREY)
    write("Press A to finish", color=GREY)
    write("")
    
    # Keep track of temporary alignment during calibration
    temp_alignment = MOTOR_ALIGNMENT
    
    while not is_pressed(BUTTON_A):
        # Show current alignment value
        #write(f"Alignment: {temp_alignment:+3d}", color=YELLOW, line=6)
        write(temp_alignment, color=YELLOW)
        
        # Drive forward to test alignment
        motor('forward', speed, 'forward', speed)
        
        # Check for button presses
        if is_pressed(BUTTON_LEFT):
            temp_alignment = max(-100, temp_alignment - 1)
            MOTOR_ALIGNMENT = temp_alignment
            write("LEFT", color=GREY)
            beep(1000, 100)  
        elif is_pressed(BUTTON_RIGHT):
            temp_alignment = min(100, temp_alignment + 1)
            MOTOR_ALIGNMENT = temp_alignment
            write("RIGHT", color=GREY)
            beep(1500, 100)  
            
        sleep(0.05)
    
    # Stop motors when done
    stop()
    reset_terminal()
    beep(1300)  # Confirmation beep
    write("Alignment complete!", color=GREEN)
    write(f"Alignment: {MOTOR_ALIGNMENT:+3d}", color=YELLOW)
    
    # Save alignment to config
    if config_set('MOTOR_ALIGNMENT', MOTOR_ALIGNMENT):
        write("Saved in config.ini", color=GREEN)
    else:
        write("Error saving config", color=RED)
    
    sleep(1)

def motor(direction_left, speed_left, direction_right, speed_right):
    """Control both motors simultaneously
    direction_left/right: 'forward'/'backward' or None for stop
    speed_left/right: 0-100"""
    
    # Apply motor alignment adjustment
    if speed_left > 0 and speed_right > 0:
        if MOTOR_ALIGNMENT < 0:
            speed_left = max(0, speed_left * (1 + MOTOR_ALIGNMENT/100))
        elif MOTOR_ALIGNMENT > 0:
            speed_right = max(0, speed_right * (1 - MOTOR_ALIGNMENT/100))
    
    # Apply battery voltage compensation for motors to compensate for weak battery
    voltage = battery_voltage_read()
    # Nominal voltage is around 6V for 4 AAA batteries
    # Scale up speed as voltage drops from 6V to 4.7V
    if voltage < 6.0:
        compensation = min(6.0 / max(voltage, 4.7), 1.3)  # Max 30% boost
        speed_left = min(100, speed_left * compensation)
        speed_right = min(100, speed_right * compensation)
    
    # Convert speeds to duty cycles
    left_duty = int(speed_left * 1023 / 100) if speed_left > 0 else 0
    right_duty = int(speed_right * 1023 / 100) if speed_right > 0 else 0
    left_kick_duty = int(KICK_START_SPEED * 1023 / 100) if speed_left > 0 else 0
    right_kick_duty = int(KICK_START_SPEED * 1023 / 100) if speed_right > 0 else 0
    
    # Set kick-start duty for both motors (only if speed > 0)
    if speed_left > 0:
        if direction_left == 'forward':
            INT1_A.duty(left_kick_duty)
            INT2_A.duty(0)
        elif direction_left == 'backward':
            INT1_A.duty(0)
            INT2_A.duty(left_kick_duty)
    else:  # stop
        INT1_A.duty(0)
        INT2_A.duty(0)
        
    if speed_right > 0:
        if direction_right == 'forward':
            INT1_B.duty(right_kick_duty)
            INT2_B.duty(0)
        elif direction_right == 'backward':
            INT1_B.duty(0)
            INT2_B.duty(right_kick_duty)
    else:  # stop
        INT1_B.duty(0)
        INT2_B.duty(0)
        
    # Apply kick-start delay if either motor is moving
    if speed_left > 0 or speed_right > 0:
        time.sleep_ms(KICK_START_DURATION_MS)
        
    # Set normal speed for both motors
    if speed_left > 0:
        if direction_left == 'forward':
            INT1_A.duty(left_duty)
            INT2_A.duty(0)
        elif direction_left == 'backward':
            INT1_A.duty(0)
            INT2_A.duty(left_duty)
    else:
        INT1_A.duty(0)
        INT2_A.duty(0)
        
    if speed_right > 0:
        if direction_right == 'forward':
            INT1_B.duty(right_duty)
            INT2_B.duty(0)
        elif direction_right == 'backward':
            INT1_B.duty(0)
            INT2_B.duty(right_duty)
    else:
        INT1_B.duty(0)
        INT2_B.duty(0)
        
    if speed_left > 0 or speed_right > 0:
        time.sleep_ms(MIN_DURATION_MS)

def forward(speed=10):
    """Move forward with kick-start"""
    motor('forward', speed, 'forward', speed)
    
def backward(speed=10):
    """Move backward with kick-start"""
    motor('backward', speed, 'backward', speed)
    
def turn(speed=30, direction=None):
    if direction == False or direction == 0 or direction == 'L':
        turn_left(speed)
    else:
        turn_right(speed)
    
def turn_left(speed=20):
    motor('forward', 0, 'forward', speed)
    
def turn_right(speed=20):
    motor('forward', speed, 'forward', 0)   
    
def turn_random(speed=20):
    """Turn in a random direction with specified speed"""
    import random
    if random.choice([True, False]):
        turn_left(speed)
    else:
        turn_right(speed)

def stop():
    motor(None, 0, None, 0)

stop()    
            
            
### SOUND
# Connecter beeper minus to ground
# Connect beeper plus to a GPIO pin

# Initialize the beeper on a specific GPIO pin
beeper = PWM(Pin(26))

# Function to beep, duty = volume/loudness
def beep(frequencey = 1000, duration_ms = 250, duty = 256):
    beeper.freq(frequencey)  # Set frequency (1000 Hz is a typical beeper frequency)
    beeper.duty(duty)  # Set duty cyle to control volume
    time.sleep_ms(duration_ms)
    beeper.duty(0)  # Set duty cycle to 0% to turn off beeper
    
def shutup():
    beeper.duty(0)  # Set duty cycle to 0% to turn off beeper
    
shutup()    
    
# def siren():
#     for _ in range(2):  # Number of siren cycles
#         beeper.freq(1000)  # First frequency
#         beeper.duty(512)  # Turn on beeper
#         time.sleep(0.5)  # Duration of the first tone
#         beeper.freq(500)  # Second frequency
#         time.sleep(0.5)  # Duration of the second tone
#     beeper.duty(0)  # Turn off beeper
    
def sweep():
    # Sweep up in frequency
    for freq in range(500, 2001, 100):  # Start at 500 Hz, go up to 2000 Hz
        beep(freq, 25)

    # Sweep down in frequency
    for freq in range(2000, 499, -100):  # Start at 2000 Hz, go down to 500 Hz
        beep(freq, 25)

### RGB LED
# Load RGB LED pin configuration
RGB_RED_PIN = config_get('RED_PIN')
RGB_GREEN_PIN = config_get('GREEN_PIN')
RGB_BLUE_PIN = config_get('BLUE_PIN')

# Initialize RGB LED PWM pins
rgb_led_red = PWM(Pin(RGB_RED_PIN), freq=1000)
rgb_led_green = PWM(Pin(RGB_GREEN_PIN), freq=1000)
rgb_led_blue = PWM(Pin(RGB_BLUE_PIN), freq=1000)

# Function to set color using TFT color constants
def rgb_led(color):
    #print("rgb_led()", color)
    """Set RGB LED color using RGB tuple (0-255 per channel)"""
    r, g, b = color
    
    # Convert 8-bit values (0-255) to 16-bit values (0-65535) for duty_u16
    rgb_led_red.duty_u16(int(r * 65535 / 255))
    rgb_led_green.duty_u16(int(g * 65535 / 255))
    rgb_led_blue.duty_u16(int(b * 65535 / 255))
    
rgb_led(BLACK)  # Start with led off

# Displays a gradient from green to yellow to red on an RGB LED based on an input value between 0 and 255.
def visualize_value(value):
    # Ensure the input value is within 0 to 255
    value = max(0, min(255, value))
    
    if value <= 127:
        # From red to yellow: Decrease red, green starts from 0
        red = 255 - int((value / 127) * 255)
        green = int((value / 127) * 255)
    else:
        # From yellow to green: Red is 0, increase green
        red = 0
        green = int(((value - 128) / 127) * 255)
        
    #print(red,green)        
    
    # No blue component needed for this gradient
    blue = 0
    
    # Use the rgb_led function to set the color
    rgb_led((red, green, blue))
    

### INFRARED SENSORS
# Load IR sensor pin configuration
IR_LEFT_PIN = config_get('IR_LEFT_PIN')
IR_RIGHT_PIN = config_get('IR_RIGHT_PIN')

infrared_left_pin = Pin(IR_LEFT_PIN, Pin.IN)
infrared_right_pin = Pin(IR_RIGHT_PIN, Pin.IN)

# Return true/1 if the left infrared sensor detects an object
def infrared_left():
    return not infrared_left_pin.value()

# Return true/1 if the right infrared sensor detects an object
def infrared_right():
    return not infrared_right_pin.value()   

def ir_is_dark_left():
    return not infrared_left()

def ir_is_dark_right():
    return not infrared_right()

def ir_is_bright_left():
    return infrared_left()

def ir_is_bright_right():
    return infrared_right()


### SYSTEM
def get_ip():
    wlan = network.WLAN(network.STA_IF)
    return wlan.ifconfig()[0]


### FRIENDLY FUNCTIONS
def sleep(quantity, unit = "s"):
    if unit == "ms":
        return time.sleep_ms(quantity)
    
    return time.sleep(quantity)


### BUTTONS
from machine import Pin

# Load button pin configuration
BUTTON_UP = Pin(config_get('UP_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_DOWN = Pin(config_get('DOWN_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_LEFT = Pin(config_get('LEFT_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_RIGHT = Pin(config_get('RIGHT_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(config_get('A_PIN'), Pin.IN, Pin.PULL_UP)

def is_pressed(button):
    return not button.value()  # Returns True if button is pressed (low)

### NETWORK SETUP
def network_setup():
    """Setup network connection using config.ini"""
    print("Activating network")
    import network
    import ubinascii

    # Try to load configuration
    ssid = config_get('WLAN_SSID')
    password = config_get('WLAN_PASSWORD')
    
    if not ssid or not password:
        print("No valid WiFi configuration found - starting AP mode")
        write("No WiFi config", color=YELLOW)
        start_ap_mode()
        return False

    try:
        wlan = network.WLAN(network.STA_IF)
        if not wlan.active():
            wlan.active(True)
            #write("Activating WiFi...", color=GREY)
            time.sleep(0.1)  # Give WiFi some time to initialize
        
        if not wlan.isconnected():
            write("Connecting to WiFi", color=WHITE)
            write(f"{ssid}", color=CYAN)
            write("Press A to abort", color=GREY)
            wlan.connect(ssid, password)

            # Try to connect to WLAN
            start_time = time.time()
            #dots = 0
            while not wlan.isconnected() and time.time() - start_time < 30:
                # Check for abort button
                if is_pressed(BUTTON_A):
                    wlan.disconnect()
                    sleep(1)
                    break
                    
                # Show loading animation
                #write("." if dots == 0 else "", color=CYAN)
                #write(".", color=GREY)
                #dots = (dots + 1) % 3
                sleep(.2)

            #tft.fill(BLACK)  # Clear the loading animation

        if wlan.isconnected():
            mac = ubinascii.hexlify(wlan.config('mac')).decode().upper()
            mac = ":".join([mac[i:i+2] for i in range(0, len(mac), 2)])
            ip_address = wlan.ifconfig()[0]
            write("Success!", color=GREEN)
            # write("Connected to WiFi")
            # write(f"{ssid}", color=CYAN)
            write(f"MAC: {mac}", color=GREY)
            write("")  # Newline
            write("Open in your webbrowser:", color=WHITE)
            write(f"http://{ip_address}", color=CYAN)

            gc.collect()  # Force garbage collection to free memory
            
            print("\nStarting webrepl")
            try:
                import webrepl
                webrepl.start()
            except Exception as e:
                print("WebREPL error:", e)

            gc.collect()  # Force garbage collection to free memory
            
            print("Starting IDE web service")
            try:
                import weditor.start
            except Exception as e:
                print("Web editor error:", e)
            
            gc.collect()  # Force garbage collection to free memory

            return True
        else:
            print("")
            print("WiFi not connected")
            write("WiFi not connected", color=YELLOW)
            print("Starting AP mode")
            write("Starting AP mode")
            sleep(1)
                   
            start_ap_mode()
            return False
            
    except Exception as e:
        print("WiFi setup error:", e)
        start_ap_mode()
        return False 

def start_ap_mode():
    """Start access point mode with configuration portal"""
    import network
    from microWebSrv import MicroWebSrv
    
    # First scan for networks
    print("\nScanning for WiFi networks...")
    write("Scanning for WiFis...", color=GREY)
    sta_if = network.WLAN(network.STA_IF)
    print("Deactivating WiFi")
    sta_if.active(False)  # First deactivate
    time.sleep(0.5)      # Wait a bit
    print("Activating WiFi")
    sta_if.active(True)  # Then reactivate
    time.sleep(2)        # Give WiFi time to initialize
    
    networks = []
    for _ in range(3):  # Try scanning up to 3 times
        scan_result = sta_if.scan()
        networks = [net for net in scan_result if net[0] and len(net[0].strip()) > 0]
        if networks:
            break
        write("No networks found, retrying...", color=YELLOW)
        time.sleep(1)
    
    networks.sort(key=lambda x: x[3], reverse=True)  # Sort by signal strength
    
    # tft.fill(BLACK)
    # write("Available networks:", color=CYAN)
    # for net in networks[:5]:  # Show top 5 networks
    #     ssid = net[0].decode('utf-8')
    #     rssi = net[3]
    #     security = "🔒" if net[4] > 0 else "🔓"
    #     write(f"{security} {ssid:20} RSSI:{rssi:3d}dB", color=WHITE)
    
    # Then start AP
    ap = network.WLAN(network.AP_IF)
    ap.active(False)  # First deactivate
    time.sleep(0.1)   # Wait a bit
    ap.active(True)   # Then reactivate
    
    # Get last 4 characters of MAC address
    mac = ubinascii.hexlify(sta_if.config('mac')).decode()
    ap_ssid = f"XWK_BOT_{mac[-4:].upper()}"
    
    # Configure the access point
    ap.config(essid=ap_ssid,
             authmode=network.AUTH_OPEN,
             channel=1,
             hidden=False)
    
    reset_terminal()
    write("Access Point active!", color=GREEN)
    write("Please connect to Wifi:")
    write(f"{ap_ssid}", color=CYAN)

    write("")
    write("Then open in webbrowser:", color=WHITE)
    write(f"http://{ap.ifconfig()[0]}", color=CYAN)
    write("and configure your WiFi")

    # Web server route handlers
    def _httpHandlerConfig(httpClient, httpResponse):
        # Create network options HTML
        network_options = ""
        for net in networks:
            ssid = net[0].decode('utf-8')
            network_options += f'<option value="{ssid}">{ssid}</option>'

        content = f"""
        <html><head>
            <title>XWK-Bot WiFi Setup</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                select, input {{ margin: 10px 0; padding: 5px; width: 200px; }}
                form {{ max-width: 300px; margin: 0 auto; }}
            </style>
        </head><body>
            <h1>XWK-Bot WiFi Setup</h1>
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
        httpResponse.WriteResponseOk(
            contentType="text/html",
            contentCharset="UTF-8",
            content=content)

    def _httpHandlerConfigPost(httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()
        ssid = formData["ssid"]
        password = formData["password"]
        
        print(f"\nSaving WiFi configuration: {ssid}")
        write(f"Saving WiFi configuration: {ssid}", color=GREY)
        
        # Save to config.ini using our config functions
        config_set('WLAN_SSID', ssid)
        config_set('WLAN_PASSWORD', password)
        
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
        
        httpResponse.WriteResponseOk(
            headers = {"Connection": "close"},
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
    
    srv.Start(threaded=True)