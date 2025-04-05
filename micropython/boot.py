import bot                      # Load the 'lib/bot.py' library which contains all XWK-Bot functions

bot.shutup()                    # Make sure the beeper is silent
bot.stop()                      # Make sure motors are stopped
bot.battery_voltage_warning()   # Check battery voltage

bot.image("/lib/logo.bin", scale=5, y=30)                        # Display the XWK logo
bot.write("    XWK-Bot says hello!", color=bot.WHITE, line=9)    # Write welcome text
bot.sleep(2)                                                     # Wait 2 seconds
bot.reset_terminal()                                             # Reset the terminal position and clear screen

# import selftest.py            # Start a program automatically (remove the '#' at the beginning of the line to enable this)

bot.network_setup()             # Setup the network
bot.write("")                   # Write an empty line to the display

import menu                     # Load the 'lib/menuy.py' library
menu.start()                    # Display the menu
