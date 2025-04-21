### MATRIX PAINTER
# Paint pictures on a color RGB led matrix
# Use left/right/up/down to move the cursor
# Use B to select the color, use A to paint

# This code is for Lolin D32 ESP WROOM 32
# If you use another microcontroller change the pin definitions accordingly

### IMPORTS
# Importing the Pin class from the machine module
# The machine module is typically used for hardware-related functionalities on microcontrollers
from machine import Pin, ADC
# Importing the neopixel module for controlling NeoPixel (WS2812) LEDs
import neopixel
# Importing the time module for handling time-related functions like sleep() or ticks_ms()
import time
# Allows to save data
import ujson



### CONSTANTS
# Constants are values that remain unchanged during the execution of the program.
# They are used to assign meaningful names to specific values, making the code more readable and maintainable
LED_PIN = 16			# The pin where the LED matrix is connected
NUM_LEDS = 64   		# Number of total leds in the matrix
MATRIX_WIDTH = 8		# Width of the matrix ("x")
MATRIX_HEIGHT = 8		# Height of the matrix ("y")

BRIGHTNESS_PIN = 32     # Brightness potentiometer
BRIGHTNESS_MAX = 100    # Maximum brightness to stay below 500mA current consumption

# Pins where the buttons are connected
BUTTON_UP_PIN = 23
BUTTON_RIGHT_PIN = 22
BUTTON_DOWN_PIN = 21
BUTTON_LEFT_PIN = 19
BUTTON_Y_PIN = 4
BUTTON_X_PIN = 0
BUTTON_B_PIN = 2
BUTTON_A_PIN = 15


# Configure the pins for the buttons to "input"
# Enable the internal pull-up resistor, so by default the button value is HIGH, when pressed LOW
# Cable the buttons with one pin to ground (minus "-") and the other pin to the microcontroller
# (Pull up is recommended because of lower power noise)
Pin(BUTTON_UP_PIN, Pin.IN, Pin.PULL_UP) 
Pin(BUTTON_RIGHT_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_DOWN_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_LEFT_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_Y_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_X_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)  


### GLOBAL VARIABLES
# Global variables are values that can be accessed and modified throughout the entire program.
# They are declared outside of any function and can be utilized by multiple functions,
# allowing information to be shared and maintained across different parts of the code.

# Creating a NeoPixel object named 'leds' to control the LED matrix.
# The NeoPixel class is initialized with the pin number (LED_PIN) to which the LED strip is connected
# and the total number of LEDs in the strip (NUM_LEDS).
leds = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)

# Create a list to hold the color values of each pixel you paint. We call this our "picture".
# Each element in the list is initialized with the RGB tuple (0, 0, 0), representing the color black.
# A tuple is like a list but no elements can be added or deleted (immutable).
picture = [(0, 0, 0)] * NUM_LEDS

# Cursor position
cursor_x = 0
cursor_y = 0

# For cursor blinking
cursor_visible = True
previous_cursor_blink_tick_ms = 0

# Help ignoring rapid button presses and therefore double moves
previous_button_tick_ms = 0

# Our color palette
colors = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 255, 255),  # White
    (0, 0, 0),      # Black
    # Add more colors as needed
]
# Holds the list index of currently selected paint color
current_color_index = 0


brightness = 25 	     					# Variable for the current brightness
brightness_pot = ADC(Pin(BRIGHTNESS_PIN))   # Create an ADC object for reading analog values
brightness_pot.width(ADC.WIDTH_10BIT)		# Set ADC resolution to 10bit
brightness_pot.atten(ADC.ATTN_11DB)  		# For correct pot range with 3.3V 

### FUNCTIONS

# Define a custom XY function to map 2D coordinates to a 1D index
def xy(x, y):
    return y * MATRIX_WIDTH + x
    

# Handle pressed buttons
def handle_button_presses():
    global cursor_x
    global cursor_y
    global current_color_index
    global previous_button_tick_ms
    
    #print("Cursor X:", cursor_x, "Cursor Y:", cursor_y)
    
    # Paint the current color at the current cursor position
    if not Pin(BUTTON_A_PIN).value():
        picture[xy(cursor_x, cursor_y)] = colors[current_color_index]
        # We want to be able to hold the paint button, so no debouncing here       

    # Debouncing mechanism: wait for a short time before processing another button press
    if time.ticks_ms() - previous_button_tick_ms <= 150:
        # Ignore rapid button presses
        return

    # Move the cursor up, down, left, and right
    if not Pin(BUTTON_LEFT_PIN).value() and cursor_x > 0:
        cursor_x -= 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(BUTTON_RIGHT_PIN).value() and cursor_x < MATRIX_WIDTH - 1:
        cursor_x += 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(BUTTON_UP_PIN).value() and cursor_y > 0:
        cursor_y -= 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(BUTTON_DOWN_PIN).value() and cursor_y < MATRIX_HEIGHT - 1:
        cursor_y += 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press

    # Change the current color
    if not Pin(BUTTON_B_PIN).value():
        # Move to the next color in the array
        current_color_index = (current_color_index + 1) % len(colors)
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    # Clear the picture
    if not Pin(BUTTON_X_PIN).value():
        for i in range(NUM_LEDS):
            picture[i] = (0, 0, 0)        
        previous_button_millis = time.ticks_ms()  # Remember the time of this button press

    # Save the picture to file
    if not Pin(BUTTON_Y_PIN).value():
        save_to_file()
        previous_button_millis = time.ticks_ms()  # Remember the time of this button press

        


# Update the led matrix
def update_matrix():
    
    # Copy picture data to the leds
    for i in range(NUM_LEDS):
        leds[i] = picture[i]
    # Paint the cursor (blinking)
    if cursor_visible:
        leds[xy(cursor_x, cursor_y)] = colors[current_color_index]
    else:
        leds[xy(cursor_x, cursor_y)] = (15, 15, 15)  # Dark grey   
    
    set_matrix_brightness()      

    # Output the "leds" data to the LED matrix
    leds.write()


# Use a timer to check if we should change the cursor visible or not visible state
def blink_cursor():
    global previous_cursor_blink_tick_ms
    global cursor_visible

    current_cursor_blink_tick_ms = time.ticks_ms()

    # Blink the cursor every 250 milliseconds
    if current_cursor_blink_tick_ms - previous_cursor_blink_tick_ms >= 150:
        cursor_visible = not cursor_visible
        previous_cursor_blink_tick_ms = current_cursor_blink_tick_ms  # Reset the timer


# Set brightness level of LED matrix (0-255)
def set_matrix_brightness():
    global brightness
    
    # Map analog value from 0 to max brightness (current limit)
    brightness = int(brightness_pot.read() / 1023 * BRIGHTNESS_MAX) 
    #print("Pot:", brightness_pot.read(), "brightness:", brightness);
                
    brightness = 1 if brightness == 0 else brightness	# set minimum brightness to 1
    
    for i in range(NUM_LEDS):
        # Dim each pixel by scaling its RGB values
        leds[i] = tuple(int(c * brightness / 255) for c in leds[i])


def load_from_file():
    try:
        with open("picture.json", "r") as file:
            loaded_data = ujson.load(file)
            for i in range(min(NUM_LEDS, len(loaded_data))):
                picture[i] = tuple(loaded_data[i])
    except OSError:
        pass  # File does not exist or cannot be read


def save_to_file():
    with open("picture.json", "w") as file:
        ujson.dump(picture, file)
        
"""        
def blend_to_color(target_color, steps=30):
    global leds, picture
    
    # Calculate the initial differences and the step increments for each pixel
    step_increments = []
    for i in range(NUM_LEDS):
        r_current, g_current, b_current = picture[i]
        r_target, g_target, b_target = target_color
        
        # Calculate the difference and step increment
        r_diff = (r_target - r_current) // steps
        g_diff = (g_target - g_current) // steps
        b_diff = (b_target - b_current) // steps
        
        # Store the increments for later use
        step_increments.append((r_diff, g_diff, b_diff))
    
    # Apply the increments over the specified number of steps
    for step in range(steps):
        for i in range(NUM_LEDS):
            r_current, g_current, b_current = picture[i]
            r_increment, g_increment, b_increment = step_increments[i]
            
            # Apply the increment
            r_next = r_current + r_increment
            g_next = g_current + g_increment
            b_next = b_current + b_increment
            
            # Ensure the color does not exceed or fall below the target on the final step
            if step == steps - 1:
                r_next, g_next, b_next = target_color  # Set directly to target to avoid minor discrepancies
            
            # Update the current color
            new_color = (r_next, g_next, b_next)
            picture[i] = new_color
            leds[i] = new_color
            
            # Optional: print the new color for debugging
            print("Step", step, "Pixel", i, "New Color", new_color)
            
                 
        set_matrix_brightness()       
        leds.write()  # Update the LEDs
        time.sleep(0.05)  # Small delay to visualize transition
"""

def blend_to_color(target_color, steps=30):
    global leds, picture
    
    # Calculate the initial differences and the proportional step increments for each pixel
    step_increments = []
    for i in range(NUM_LEDS):
        r_current, g_current, b_current = picture[i]
        r_target, g_target, b_target = target_color
        
        # Calculate the difference and step increment, using float division for smoother transitions
        r_diff = (r_target - r_current) / float(steps)
        g_diff = (g_target - g_current) / float(steps)
        b_diff = (b_target - b_current) / float(steps)
        
        # Store the increments for later use
        step_increments.append((r_diff, g_diff, b_diff))
    
    # Apply the increments over the specified number of steps
    for step in range(steps):
        for i in range(NUM_LEDS):
            r_current, g_current, b_current = picture[i]
            r_increment, g_increment, b_increment = step_increments[i]
            
            # Apply the increment and use int to round down
            r_next = int(r_current + r_increment)
            g_next = int(g_current + g_increment)
            b_next = int(b_current + b_increment)
            
            # Clamp values to avoid going below 0 or above 255
            r_next = max(0, min(255, r_next))
            g_next = max(0, min(255, g_next))
            b_next = max(0, min(255, b_next))
            
            # Ensure the color does not exceed or fall below the target on the final step
            if step == steps - 1:
                r_next, g_next, b_next = target_color  # Set directly to target to avoid minor discrepancies
            
            # Update the current color
            new_color = (r_next, g_next, b_next)
            picture[i] = new_color
            leds[i] = new_color
            
            # Optional: print the new color for debugging
            #print("Step", step, "Pixel", i, "New Color", new_color)
        
        set_matrix_brightness()       
        leds.write()  # Update the LEDs
        #time.sleep(0.05)  # Small delay to visualize transition

        
    

# Load saved picture at startup
load_from_file()

blend_to_color((0, 0, 0))



### THE MAIN LOOP
# Run the main loop indefinitely
while True:    
    # Update cursor position based on button presses
    handle_button_presses()

    # Blink the cursor
    blink_cursor()
    
    # Update the LED matrix
    update_matrix()        


