import bot
import sys

bot.write("selftest.py", color=bot.MAGENTA)
bot.write("")


# IR Sensor Test
bot.write("Testing IR sensors...", color=bot.CYAN)
bot.write("Press A to abort", color=bot.GREY)
count = 0
while not bot.is_pressed(bot.BUTTON_A):
    if count == 5:
        bot.write("Left: ", color=bot.GREY, newline=False)
        if (bot.ir_is_bright_left()):
            bot.write("bright", color=bot.YELLOW, newline=False)
        else:
            bot.write("dark  ", color=bot.BLUE, newline=False)
        
        bot.write(" Right: ", color=bot.GREY, newline=False)
        if (bot.ir_is_bright_right()):
            bot.write("bright", color=bot.YELLOW, newline=False)
        else:
            bot.write("dark  ", color=bot.BLUE, newline=False)
        
        bot.write("")
        count = 0
    #endif

    count += 1
    bot.sleep(0.1)

# endwhile    
bot.write("IR test complete", color=bot.GREEN)
bot.sleep(2)
bot.reset_terminal()


# Ultrasonic Sensor Test
bot.write("Testing ultrasonic sensor...", color=bot.CYAN)
bot.write("Press A to abort", color=bot.GREY)
count = 0
while not bot.is_pressed(bot.BUTTON_A):
    if count == 5:
        distance = bot.distance()
        if distance is not None:
            bot.write(f"Distance: {distance} cm", color=bot.YELLOW)
        else:
            bot.write("Error reading distance", color=bot.RED)
        count = 0
    #endif

    count += 1  
    bot.sleep(0.1)

bot.write("Ultrasonic test complete", color=bot.GREEN)
bot.sleep(2)
bot.reset_terminal()

#sys.exit()

# Motor Test
bot.write("Testing motors...", color=bot.CYAN)
bot.sleep(1)

# Test left motor
bot.write("Left motor forward", color=bot.YELLOW)
bot.motor('forward', 40, None, 0)
bot.sleep(0.20)
bot.stop()
bot.sleep(0.5)

bot.write("Left motor backward", color=bot.YELLOW)
bot.motor('backward', 40, None, 0)
bot.sleep(0.20)
bot.stop()
bot.sleep(0.5)

# Test right motor
bot.write("Right motor forward", color=bot.YELLOW)
bot.motor(None, 0, 'forward', 40)
bot.sleep(0.20)
bot.stop()
bot.sleep(0.5)

bot.write("Right motor backward", color=bot.YELLOW)
bot.motor(None, 0, 'backward', 40)
bot.sleep(0.20)
bot.stop()
bot.sleep(0.5)

bot.write("Motor test complete", color=bot.GREEN)
bot.write("")
bot.sleep(1)

bot.write("1 - 2 - 3, let's make some noise!", color=bot.CYAN)
bot.sleep(1)
bot.sweep()


# RGB LED Test
COLOR_NAMES = {
    bot.RED: "RED",
    bot.GREEN: "GREEN", 
    bot.BLUE: "BLUE",
    bot.YELLOW: "YELLOW",
    bot.CYAN: "CYAN",
    bot.MAGENTA: "MAGENTA",
    bot.WHITE: "WHITE",
    bot.BLACK: "BLACK"
}

bot.reset_terminal()
bot.write("Testing RGB LED...", color=bot.CYAN)
colors = [bot.RED, bot.GREEN, bot.BLUE, bot.YELLOW, bot.CYAN, bot.MAGENTA, bot.WHITE]

for color in colors:
    bot.write(f"Displaying {COLOR_NAMES[color]}", color=color)
    bot.rgb_led(color)
    bot.sleep(500, 'ms')

bot.rgb_led(bot.BLACK)  # Turn off LED after test
bot.write("RGB LED test complete", color=bot.GREEN)
bot.sleep(1)

bot.reset_terminal()
bot.write("Press all buttons", color=bot.CYAN)
bot.write("to complete the test", color=bot.CYAN)

# List of buttons and their names
buttons = [
    (bot.BUTTON_UP, "UP"),
    (bot.BUTTON_DOWN, "DOWN"),
    (bot.BUTTON_LEFT, "LEFT"),
    (bot.BUTTON_RIGHT, "RIGHT"),
    (bot.BUTTON_A, "A")
]

pressed_buttons = set()

while len(pressed_buttons) < len(buttons):
    for button, name in buttons:
        if bot.is_pressed(button):
            bot.write(f"{name} pressed", color=bot.YELLOW)
            pressed_buttons.add(name)
            bot.sleep(0.2)  # Debounce delay

bot.write("All buttons are working!", color=bot.GREEN)
bot.write("")

bot.write("Test complete!", color=bot.MAGENTA)
bot.sweep()




