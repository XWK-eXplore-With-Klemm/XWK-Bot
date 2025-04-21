### MATRIX PAINTER
# Paint pictures on a color RGB led matrix
# Press left/right/up/down to move the cursor
# Press B to select the color
# Press A to paint
# Press X to clear the picture
# Press Y to save the picture to a file

# This code is for Lolin D32 ESP WROOM 32
# If you use another microcontroller change the pin definitions accordingly

### IMPORTS
# Importing the Pin class from the machine module
# The machine module is typically used for hardware-related functionalities on microcontrollers
from machine import Pin
# Importing the time module for handling time-related functions like sleep() or ticks_ms()
import time
# Import our pixel painter library
import lib.pixel_painter_lib as pix

### GLOBAL VARIABLES
# Global variables are values that can be accessed and modified throughout the entire program.
# They are declared outside of any function and can be utilized by multiple functions,
# allowing information to be shared and maintained across different parts of the code.

# Create a list to hold the color values of each pixel you paint. We call this our "picture".
# Each element in the list is initialized with the RGB tuple (0, 0, 0), representing the color black.
# A tuple is like a list but no elements can be added or deleted (immutable).
picture = [(0, 0, 0)] * pix.NUM_LEDS

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

### FUNCTIONS

# Handle pressed buttons
def handle_button_presses():
    global cursor_x, cursor_y, current_color_index, previous_button_tick_ms
    
    # Paint the current color at the current cursor position
    if not Pin(pix.BUTTON_A_PIN).value():
        picture[pix.xy(cursor_x, cursor_y)] = colors[current_color_index]
        # We want to be able to hold the paint button, so no debouncing here       

    # Debouncing mechanism: wait for a short time before processing another button press
    if time.ticks_ms() - previous_button_tick_ms <= 150:
        # Ignore rapid button presses
        return

    # Move the cursor up, down, left, and right
    if not Pin(pix.BUTTON_LEFT_PIN).value() and cursor_x > 0:
        cursor_x -= 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(pix.BUTTON_RIGHT_PIN).value() and cursor_x < pix.MATRIX_WIDTH - 1:
        cursor_x += 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(pix.BUTTON_UP_PIN).value() and cursor_y > 0:
        cursor_y -= 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    if not Pin(pix.BUTTON_DOWN_PIN).value() and cursor_y < pix.MATRIX_HEIGHT - 1:
        cursor_y += 1
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press

    # Change the current color
    if not Pin(pix.BUTTON_B_PIN).value():
        # Move to the next color in the array
        current_color_index = (current_color_index + 1) % len(colors)
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press
        
    # Clear the picture
    if not Pin(pix.BUTTON_X_PIN).value():
        for i in range(pix.NUM_LEDS):
            picture[i] = (0, 0, 0)        
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press

    # Save the picture to file
    if not Pin(pix.BUTTON_Y_PIN).value():
        pix.save_to_file(picture)
        previous_button_tick_ms = time.ticks_ms()  # Remember the time of this button press

# Update the led matrix
def update_matrix():
    # Copy picture data to the leds
    for i in range(pix.NUM_LEDS):
        pix.leds[i] = picture[i]
    # Paint the cursor (blinking)
    if cursor_visible:
        pix.leds[pix.xy(cursor_x, cursor_y)] = colors[current_color_index]
    else:
        pix.leds[pix.xy(cursor_x, cursor_y)] = (15, 15, 15)  # Dark grey   
    
    pix.write_leds()

# Use a timer to check if we should change the cursor visible or not visible state
def blink_cursor():
    global previous_cursor_blink_tick_ms, cursor_visible

    current_time = time.ticks_ms()

    # Blink the cursor every 150 milliseconds
    if current_time - previous_cursor_blink_tick_ms >= 150:
        cursor_visible = not cursor_visible
        previous_cursor_blink_tick_ms = current_time  # Reset the timer

### THE MAIN LOOP
# Load saved picture at startup
picture = pix.load_from_file("picture.json", picture)
pix.blend((0, 0, 0), picture, 20)

# Run the main loop indefinitely
while True:    
    # Update cursor position based on button presses
    handle_button_presses()

    # Blink the cursor
    blink_cursor()
    
    # Update the LED matrix
    update_matrix()


