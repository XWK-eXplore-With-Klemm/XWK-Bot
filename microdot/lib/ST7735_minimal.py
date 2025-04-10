# Minimal ST7735 driver for XWK-Bot
# Stripped down version of the original ST7735.py
# Only contains functions used by bot.py

import machine
import time

# Screen size and rotation constants
ScreenSize = (128, 160)
TFTRotations = [0x00, 0x60, 0xC0, 0xA0]
TFTBGR = 0x08
TFTRGB = 0x00

def TFTColor(aR, aG, aB):
    '''Create a 16 bit rgb value from the given R,G,B from 0-255.
       This assumes rgb 565 layout and will be incorrect for bgr.'''
    return ((aR & 0xF8) << 8) | ((aG & 0xFC) << 3) | (aB >> 3)

class TFT:
    # Command constants - only the ones we actually use
    SWRESET = 0x01
    SLPOUT = 0x11
    NORON = 0x13
    INVOFF = 0x20
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    MADCTL = 0x36
    COLMOD = 0x3A

    # Basic color definitions
    BLACK = 0
    WHITE = TFTColor(255, 255, 255)

    def __init__(self, spi, aDC, aReset, aCS):
        self._size = ScreenSize
        self._offset = bytearray([0, 0])
        self.rotate = 0
        self._rgb = True
        
        # Pin setup
        self.dc = machine.Pin(aDC, machine.Pin.OUT, machine.Pin.PULL_DOWN)
        self.reset = machine.Pin(aReset, machine.Pin.OUT, machine.Pin.PULL_DOWN)
        self.cs = machine.Pin(aCS, machine.Pin.OUT, machine.Pin.PULL_DOWN)
        self.cs(1)
        self.spi = spi
        
        # Buffers
        self.colorData = bytearray(2)
        self.windowLocData = bytearray(4)
        
        # Terminal settings
        self.terminal_line_height = 10
        self.terminal_max_lines = 13
        self.terminal_current_line = 0
        self.terminal_current_col = 0

    def rgb(self, aTF=True):
        '''True = rgb else bgr'''
        self._rgb = aTF
        self._setMADCTL()

    def rotation(self, aRot):
        '''0 - 3. Starts vertical with top toward pins and rotates 90 deg clockwise'''
        if 0 <= aRot < 4:
            rotchange = self.rotate ^ aRot
            self.rotate = aRot
            if rotchange & 1:
                self._size = (self._size[1], self._size[0])
            self._setMADCTL()

    def fill(self, aColor=BLACK):
        '''Fill screen with the given color.'''
        self._setwindowloc((0, 0), (self._size[0] - 1, self._size[1] - 1))
        self._setColor(aColor)
        numPixels = self._size[0] * self._size[1]
        self._draw(numPixels)

    def terminal(self, aString, aColor, aFont, newline=True, line=None):
        """Write text to terminal."""
        if self.terminal_current_line >= self.terminal_max_lines:
            self.terminal_reset()

        write_line = line if line is not None else self.terminal_current_line
        
        if newline or line is not None:
            self.terminal_current_col = 0

        self.text((self.terminal_current_col, write_line * self.terminal_line_height), 
                 str(aString), aColor, aFont)
        
        if not newline:
            self.terminal_current_col += len(str(aString)) * (aFont['Width'] + 1)
        else:
            self.terminal_current_col = 0
            if line is None:
                self.terminal_current_line += 1

    def terminal_reset(self):
        """Reset terminal state"""
        self.fill(TFT.BLACK)
        self.terminal_current_line = 0
        self.terminal_current_col = 0

    def text(self, aPos, aString, aColor, aFont):
        '''Draw text at the given position'''
        if not aFont:
            return

        px, py = aPos
        width = aFont["Width"] + 1
        
        for c in aString:
            self.char((px, py), c, aColor, aFont)
            px += width

    def char(self, aPos, aChar, aColor, aFont):
        '''Draw a character'''
        if not aFont:
            return

        startchar = aFont['Start']
        endchar = aFont['End']
        ci = ord(aChar)
        
        if startchar <= ci <= endchar:
            fontw = aFont['Width']
            fonth = aFont['Height']
            ci = (ci - startchar) * fontw
            
            charA = aFont["Data"][ci:ci + fontw]
            buf = bytearray(2 * fonth * fontw)
            
            for q in range(fontw):
                c = charA[q]
                for r in range(fonth):
                    if c & 0x01:
                        pos = 2 * (r * fontw + q)
                        buf[pos] = aColor >> 8
                        buf[pos + 1] = aColor & 0xff
                    c >>= 1
                    
            self.image(aPos[0], aPos[1], aPos[0] + fontw - 1, aPos[1] + fonth - 1, buf)

    def image(self, x0, y0, x1, y1, data):
        '''Display image data in the specified window'''
        self._setwindowloc((x0, y0), (x1, y1))
        self._writedata(data)

    def initr(self):
        '''Initialize display - red tab version'''
        self._reset()
        
        # Basic initialization sequence
        self._writecommand(TFT.SWRESET)
        time.sleep_us(150)
        self._writecommand(TFT.SLPOUT)
        time.sleep_us(500)
        
        # Set color mode to 16-bit
        self._writecommand(TFT.COLMOD)
        self._writedata(bytearray([0x05]))
        
        # Set MADCTL
        self._setMADCTL()
        
        # Turn on display
        self._writecommand(TFT.NORON)
        time.sleep_us(10)
        self._writecommand(TFT.DISPON)
        time.sleep_us(100)
        
        self.cs(1)

    def _reset(self):
        '''Reset the display'''
        self.dc(0)
        self.reset(1)
        time.sleep_us(500)
        self.reset(0)
        time.sleep_us(500)
        self.reset(1)
        time.sleep_us(500)

    def _setColor(self, aColor):
        '''Set current color for filling'''
        self.colorData[0] = aColor >> 8
        self.colorData[1] = aColor
        self.buf = bytes(self.colorData) * 32

    def _draw(self, aPixels):
        '''Send given color to the device aPixels times'''
        self.dc(1)
        self.cs(0)
        for i in range(aPixels//32):
            self.spi.write(self.buf)
        rest = (int(aPixels) % 32)
        if rest > 0:
            buf2 = bytes(self.colorData) * rest
            self.spi.write(buf2)
        self.cs(1)

    def _setwindowloc(self, aPos0, aPos1):
        '''Set a rectangular area for drawing'''
        self._writecommand(TFT.CASET)
        self.windowLocData[0] = self._offset[0]
        self.windowLocData[1] = self._offset[0] + int(aPos0[0])
        self.windowLocData[2] = self._offset[0]
        self.windowLocData[3] = self._offset[0] + int(aPos1[0])
        self._writedata(self.windowLocData)

        self._writecommand(TFT.RASET)
        self.windowLocData[0] = self._offset[1]
        self.windowLocData[1] = self._offset[1] + int(aPos0[1])
        self.windowLocData[2] = self._offset[1]
        self.windowLocData[3] = self._offset[1] + int(aPos1[1])
        self._writedata(self.windowLocData)

        self._writecommand(TFT.RAMWR)

    def _writecommand(self, aCommand):
        '''Write command to the device'''
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([aCommand]))
        self.cs(1)

    def _writedata(self, aData):
        '''Write data to the device'''
        self.dc(1)
        self.cs(0)
        self.spi.write(aData)
        self.cs(1)

    def _setMADCTL(self):
        '''Set screen rotation and RGB/BGR format'''
        self._writecommand(TFT.MADCTL)
        rgb = TFTRGB if self._rgb else TFTBGR
        self._writedata(bytearray([TFTRotations[self.rotate] | rgb])) 