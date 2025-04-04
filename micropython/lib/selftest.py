import bot

bot.write("selftest.py", color=bot.PURPLE)
bot.write("")
bot.sleep(1)

bot.write("1 - 2 - 3, let's make some noise!", color=bot.RED)
bot.sleep(1)
bot.sweep()

bot.write("Press all buttons to complete the test", color=bot.GREEN)

# List of buttons and their names
buttons = [
    (bot.BUTTON_UP, "UP"),
    (bot.BUTTON_DOWN, "DOWN"),
    (bot.BUTTON_LEFT, "LEFT"),
    (bot.BUTTON_RIGHT, "RIGHT"),
    (bot.BUTTON_A, "A")#,
    #(bot.BUTTON_B, "B")
]

pressed_buttons = set()

while len(pressed_buttons) < len(buttons):
    for button, name in buttons:
        if bot.is_pressed(button):
            bot.write(f"{name} pressed", color=bot.YELLOW)
            pressed_buttons.add(name)
            bot.sleep(0.2)  # Debounce delay

bot.write("All buttons tested successfully!", color=bot.GREEN)
bot.sweep()



