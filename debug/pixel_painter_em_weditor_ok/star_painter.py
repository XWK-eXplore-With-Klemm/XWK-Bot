### XMAS 2024 RGB WAVE PAINTER ###

"""
Press left, right to change the color
Press up, down to change the speed
Press A to exit animation and switch 
to painting mode

Use cursor keys to move the cursor
Press A to paint
Press B to select the color (only black and white)
Press X to clear the picture
Press Y to save the picture

Turn off/on to restart into 
animation mode with saved picture
"""

from machine import Pin
import time
import random
import lib.pixel_painter_lib as pix

### GLOBAL VARIABLES
picture = [(0, 0, 0)] * pix.NUM_LEDS

# Cursor position and state
cursor_x = 0
cursor_y = 0
cursor_visible = True
previous_cursor_blink_tick_ms = 0
previous_button_tick_ms = 0

# Color palette
colors = [
    (255, 255, 255),  # White
    (0, 0, 0),      # Black
]
current_color_index = 0

def handle_button_presses():
    global cursor_x, cursor_y, current_color_index, previous_button_tick_ms
    
    if not Pin(pix.BUTTON_A_PIN).value():
        picture[pix.xy(cursor_x, cursor_y)] = colors[current_color_index]

    if time.ticks_ms() - previous_button_tick_ms <= 150:
        return

    if not Pin(pix.BUTTON_LEFT_PIN).value() and cursor_x > 0:
        cursor_x -= 1
        previous_button_tick_ms = time.ticks_ms()
        
    if not Pin(pix.BUTTON_RIGHT_PIN).value() and cursor_x < pix.MATRIX_WIDTH - 1:
        cursor_x += 1
        previous_button_tick_ms = time.ticks_ms()
        
    if not Pin(pix.BUTTON_UP_PIN).value() and cursor_y > 0:
        cursor_y -= 1
        previous_button_tick_ms = time.ticks_ms()
        
    if not Pin(pix.BUTTON_DOWN_PIN).value() and cursor_y < pix.MATRIX_HEIGHT - 1:
        cursor_y += 1
        previous_button_tick_ms = time.ticks_ms()

    if not Pin(pix.BUTTON_B_PIN).value():
        current_color_index = (current_color_index + 1) % len(colors)
        previous_button_tick_ms = time.ticks_ms()
        
    if not Pin(pix.BUTTON_X_PIN).value():
        for i in range(pix.NUM_LEDS):
            picture[i] = (0, 0, 0)        
        previous_button_tick_ms = time.ticks_ms()

    if not Pin(pix.BUTTON_Y_PIN).value():
        pix.save_to_file(picture, "star.json")
        previous_button_tick_ms = time.ticks_ms()

def update_matrix():
    """Update the LED matrix with picture and cursor"""
    for i in range(pix.NUM_LEDS):
        pix.leds[i] = picture[i]

    if cursor_visible:
        pix.leds[pix.xy(cursor_x, cursor_y)] = colors[current_color_index]
    else:
        pix.leds[pix.xy(cursor_x, cursor_y)] = (15, 15, 15)
    
    pix.write_leds()

def blink_cursor():
    global previous_cursor_blink_tick_ms, cursor_visible
    current_time = time.ticks_ms()
    if current_time - previous_cursor_blink_tick_ms >= 150:
        cursor_visible = not cursor_visible
        previous_cursor_blink_tick_ms = current_time

def animate_star_pulse(initial_hue=128):
    star_pixels = []
    center_x = 3
    center_y = 3
    
    hue = initial_hue
    wave_speed = 0.085
    
    for x in range(pix.MATRIX_WIDTH):
        for y in range(pix.MATRIX_HEIGHT):
            if picture[pix.xy(x, y)] == (255, 255, 255):
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                star_pixels.append((x, y, dist))
    
    star_pixels.sort(key=lambda p: p[2])
    max_dist = star_pixels[-1][2] if star_pixels else 1
    
    wave_pos = -2
    auto_mode = True
    
    while True:
        if not Pin(pix.BUTTON_A_PIN).value():
            return
            
        if not Pin(pix.BUTTON_LEFT_PIN).value():
            auto_mode = False
            hue = (hue - 16) % 255
            print(f"H:{hue} S:{wave_speed:.3f}")
            time.sleep_ms(20)
            
        if not Pin(pix.BUTTON_RIGHT_PIN).value():
            auto_mode = False
            hue = (hue + 16) % 255
            print(f"H:{hue} S:{wave_speed:.3f}")
            time.sleep_ms(20)
            
        if not Pin(pix.BUTTON_UP_PIN).value():
            auto_mode = False
            wave_speed = min(0.3, wave_speed + 0.01)
            print(f"H:{hue} S:{wave_speed:.3f}")
            time.sleep_ms(20)
            
        if not Pin(pix.BUTTON_DOWN_PIN).value():
            auto_mode = False
            wave_speed = max(0.02, wave_speed - 0.01)
            print(f"H:{hue} S:{wave_speed:.3f}")
            time.sleep_ms(20)
        
        wave_pos += wave_speed
        if wave_pos > max_dist + 2:
            wave_pos = -2
            if auto_mode:
                hue = random.randint(0, 255)
                print(f"H:{hue} S:{wave_speed:.3f}")
        
        for x, y, dist in star_pixels:
            diff = abs(dist - wave_pos)
            if diff < 3:
                brightness = max(0, min(255, int(255 * (1 - diff/3))))
                saturation = 255 - (brightness // 2)
                pix.leds[pix.xy(x, y)] = pix.hsv_to_rgb(hue, saturation, brightness)
            else:
                pix.leds[pix.xy(x, y)] = (0, 0, 0)
        
        pix.write_leds()
        time.sleep_ms(35)

#### MAIN CODE ####

# Load the saved 1-bit image
picture = pix.load_from_file("star.json")

# Start animation
animate_star_pulse(128)

pix.blend("leds", (0, 0, 0), 10)
pix.fill((0, 0, 0))
time.sleep(0.5)

picture = pix.load_from_file("star.json")
pix.blend((0, 0, 0), picture, 10)

# Switch to drawing mode
while True:    
    handle_button_presses()
    blink_cursor()
    update_matrix()
