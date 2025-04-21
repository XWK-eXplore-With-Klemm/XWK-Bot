### RAINBOW TREE ANIMATION
# Displays a rainbow-colored tree pattern
# Uses the pixel painter library for LED matrix control

print("Rainbowtree")

### IMPORTS
import time
import lib.pixel_painter_lib as pix

### GLOBAL VARIABLES
picture = [(0, 0, 0)] * pix.NUM_LEDS

def rainbow_color(pos):
    """Generate rainbow colors using position"""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def display_rainbow(offset):
    """Display the tree pattern with rainbow colors"""
    # Define the correct "21" pattern
    pattern = [
        0,0,0,1,0,0,0,0,
        0,0,1,1,1,0,0,0,
        0,0,1,1,1,0,0,0,
        0,1,1,1,1,1,0,0,
        0,1,1,1,1,1,0,0,
        1,1,1,1,1,1,1,0,
        1,1,1,1,1,1,1,0,
        0,0,0,1,0,0,0,0
    ]
    
    for i, pixel in enumerate(pattern):
        if pixel:
            color = rainbow_color((i * 4 + offset) % 256)  # Restored to original speed
            pix.leds[i] = color
        else:
            pix.leds[i] = (0, 0, 0)
    pix.write_leds()

### MAIN CODE

# Animate the "21"
offset = 0
while True:
    display_rainbow(offset)
    offset = (offset + 1) % 256  # Restored to original increment
    time.sleep(0.001)  # Restored to original delay

