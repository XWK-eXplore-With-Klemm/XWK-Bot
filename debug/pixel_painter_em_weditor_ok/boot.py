# This file is executed on every start of the ESP32 microcontroller

# Import libraries
import lib.pixel_painter_lib as pix

# Show XWK logo (intro)
pix.xwk_intro()

# Setup Wifi network
pix.network_setup()

# This is a message to debug output (shell / terminal / REPL)
print("Starting custom program") 

# Start this program automatically:
import rainbowtree.py