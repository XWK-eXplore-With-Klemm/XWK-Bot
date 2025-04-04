import bot

bot.shutup()
bot.stop()
bot.battery_voltage_warning()

bot.write("XWK-Bot says hello!")
bot.write("")

# Start a program automatically
# import selftest.py

bot.network_setup()
bot.write("")

import menu
menu.start()
