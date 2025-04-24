import bot

bot.write("uss_write.py", color=bot.MAGENTA)

while True:
    distance = bot.distance()
    bot.write("Distance: ", distance, "cm", color=bot.YELLOW)
    bot.visualize_value(distance)
    bot.beep(distance * 50, 50, 10)
    
    bot.sleep(250, "ms")

