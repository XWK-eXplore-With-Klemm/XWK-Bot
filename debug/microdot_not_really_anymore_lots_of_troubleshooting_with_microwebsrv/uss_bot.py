import bot

bot.write("uss_bot.py", color=bot.MAGENTA)

while True:
    distance = bot.distance()
    bot.write("Distance: ", distance, "cm", color=bot.YELLOW)
    if distance > 70: 
        bot.forward(20)
    else:
        bot.turn_left()