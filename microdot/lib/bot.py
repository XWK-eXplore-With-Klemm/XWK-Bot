import gc
import machine
from machine import Pin, SPI, ADC, PWM
import time
from ST7735_minimal import TFT, TFTColor # GMT-177-01 128x160px TFTST7735 display
from sysfont import sysfont
import hcsr04 # ultra sound HC-SR04 sensor
import os
from iniconf import Iniconf
from math import sqrt

### CONFIG HANDLING
# Initialize config manager
config = Iniconf()

### DISPLAY
# Load display pin configuration
SCK_PIN = config.get('SCK_PIN')
SDA_PIN = config.get('SDA_PIN')
DC_PIN = config.get('DC_PIN')
RESET_PIN = config.get('RESET_PIN')
CS_PIN = config.get('CS_PIN')

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

def clear():
    tft.terminal_reset()

def image(filepath, scale=5, x=None, y=None):
    """Display a raw RGB565 image file on the screen
    
    Args:
        filepath: Absolute path to the raw RGB565 image file
        scale: Optional scaling factor (1 = original size)
        x: Optional x coordinate for top-left position (centers if None)
        y: Optional y coordinate for top-left position (centers if None)
        
    File Format:
        - Bytes 0-1: Width (16-bit unsigned integer, big-endian)
        - Bytes 2-3: Height (16-bit unsigned integer, big-endian)
        - Bytes 4+: RGB565 pixel data (2 bytes per pixel)
    """
    try:
        # Read header and dimensions
        with open(filepath, 'rb') as f:
            # Read header (4 bytes)
            header = bytearray(4)
            for i in range(4):
                header[i] = ord(f.read(1))
                
            original_width = (header[0] << 8) | header[1]   # Big-endian 16-bit width
            height = (header[2] << 8) | header[3]           # Big-endian 16-bit height
            
            # Verify reasonable dimensions
            if original_width <= 0 or height <= 0 or original_width > 1000 or height > 1000:
                raise ValueError(f"Invalid image dimensions: {original_width}x{height}")
            
            # Calculate scaled dimensions
            scaled_width = original_width * scale
            scaled_height = height * scale
            
            # Use provided position or center if None
            if x is None:
                x = (tft._size[0] - scaled_width) // 2
            if y is None:
                y = (tft._size[1] - scaled_height) // 2
            
            # Read image data (skipping header)
            data = f.read()
            
            if scale == 1:
                # Display directly at 1:1 scale - fastest method
                tft._setwindowloc((x, y), (x + original_width - 1, y + height - 1))
                tft._writedata(data)
            else:
                # Scale using line buffer - good balance of speed and memory
                line_buf = bytearray(scaled_width * 2)  # 2 bytes per pixel
                
                # Scale and display one line at a time
                for sy in range(height):
                    # Get source line offset
                    src_offset = sy * original_width * 2
                    
                    # Scale this line horizontally
                    for dx in range(scaled_width):
                        # Map x coordinate back to source
                        sx = (dx * original_width) // scaled_width
                        
                        # Copy pixel from source
                        i = src_offset + (sx * 2)
                        line_buf[dx*2] = data[i]
                        line_buf[dx*2 + 1] = data[i + 1]
                    
                    # Repeat the scaled line vertically scale times
                    for dy in range(scale):
                        tft._setwindowloc(
                            (x, y + sy*scale + dy),
                            (x + scaled_width - 1, y + sy*scale + dy)
                        )
                        tft._writedata(line_buf)
            
            # Clean up memory
            gc.collect()
                    
    except Exception as e:
        print("Error displaying image:", e)

### ULTRASONIC
# Load ultrasonic pin configuration
TRIGGER_PIN = config.get('TRIGGER_PIN')
ECHO_PIN = config.get('ECHO_PIN')

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
MOTOR_ALIGNMENT = config.get('MOTOR_ALIGNMENT', default=0)

# Motor A Control Pins
# Do not use pins 15,2,0,4 -> 15 and 0 are 3.3V at boot!
MOTOR_LEFT_FORWARD_PIN = config.get('LEFT_FORWARD_PIN')
MOTOR_LEFT_BACKWARD_PIN = config.get('LEFT_BACKWARD_PIN')
MOTOR_RIGHT_FORWARD_PIN = config.get('RIGHT_FORWARD_PIN')
MOTOR_RIGHT_BACKWARD_PIN = config.get('RIGHT_BACKWARD_PIN')

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
    config.set('MOTOR_ALIGNMENT', MOTOR_ALIGNMENT)
    config.save()
    write("Saved in config.ini", color=GREEN)
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
RGB_RED_PIN = config.get('RED_PIN')
RGB_GREEN_PIN = config.get('GREEN_PIN')
RGB_BLUE_PIN = config.get('BLUE_PIN')

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
IR_LEFT_PIN = config.get('IR_LEFT_PIN')
IR_RIGHT_PIN = config.get('IR_RIGHT_PIN')

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


### ### FRIENDLY FUNCTIONS
def sleep(quantity, unit = "s"):
    if unit == "ms":
        return time.sleep_ms(quantity)
    
    return time.sleep(quantity)


### BUTTONS
from machine import Pin

# Load button pin configuration
BUTTON_UP = Pin(config.get('UP_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_DOWN = Pin(config.get('DOWN_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_LEFT = Pin(config.get('LEFT_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_RIGHT = Pin(config.get('RIGHT_PIN'), Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(config.get('A_PIN'), Pin.IN, Pin.PULL_UP)

def is_pressed(button):
    return not button.value()  # Returns True if button is pressed (low)