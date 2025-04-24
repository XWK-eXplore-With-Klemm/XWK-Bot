import bot

bot.write("linefollower.py", color=bot.MAGENTA)
bot.write("")

while True:

    if (bot.ir_is_dark_left() and bot.ir_is_dark_right()):
        bot.write("IR both DARK => STOP", color=bot.MAGENTA)
        bot.beep()
        bot.stop()
        bot.write("Press A to continue", color=bot.WHITE)
        while not bot.is_pressed(bot.BUTTON_A):
            bot.sleep(0.1)
        
        # Continue the loop instead of breaking out
        continue        

    if (bot.ir_is_dark_left()):
        bot.write("IR LEFT  detected DARK", color=bot.GREEN)
        bot.turn_left()
        
    elif (bot.ir_is_dark_right()):
        bot.write("IR RIGHT detected DARK", color=bot.RED)
        bot.turn_right()
        
    else:
        bot.forward()
        
    