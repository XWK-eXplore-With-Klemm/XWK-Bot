import bot

bot.write("uss_write.py", color=bot.MAGENTA)

while True:
    distance = bot.distance()
    bot.write("Distance: ", distance, "cm", color=bot.YELLOW)
    bot.visualize_value(distance)
    bot.beep(distance * 50, 0.05, 10)
    
    bot.sleep(0.25)

