# The MIT License (MIT)
#
# Copyright (c) 2014 Kenneth Henderick
# Revised (c) 2018 Mark Zachmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# -----------------------------------------------
# Revised for Pycom Lopy, Supports both SSD1306 and SH1106
# Removed SPI support because I have no way to test it and don't need it
# This assumes standard SDA/SCL pins but they are programmable by changing the I2cHelper class
# -----------------------------------------------

# put I2c behind a simple wrapper
from graphicslib import I2cHelper

# Constants
DISPLAYOFF          = 0xAE
SETCONTRAST         = 0x81
DISPLAYALLON_RESUME = 0xA4
DISPLAYALLON        = 0xA5
NORMALDISPLAY       = 0xA6
INVERTDISPLAY       = 0xA7
DISPLAYON           = 0xAF
SETDISPLAYOFFSET    = 0xD3
SETCOMPINS          = 0xDA
SETVCOMDETECT       = 0xDB
SETDISPLAYCLOCKDIV  = 0xD5
SETPRECHARGE        = 0xD9
SETMULTIPLEX        = 0xA8
SETLOWCOLUMN        = 0x00
SETHIGHCOLUMN       = 0x10
SETSTARTLINE        = 0x40
MEMORYMODE          = 0x20
COLUMNADDR          = 0x21
PAGEADDR            = 0x22
COMSCANINC          = 0xC0
COMSCANDEC          = 0xC8
SEGREMAP            = 0xA0
# mz-afaik the SH1106 does NOT have this instruction
# but it seems benign to program it and all the hobby chips are internal
CHARGEPUMP          = 0x8D
EXTERNALVCC         = 0x10
SWITCHCAPVCC        = 0x20
SETPAGEADDR         = 0xB0
SETCOLADDR_LOW      = 0x00
SETCOLADDR_HIGH     = 0x10
ACTIVATE_SCROLL                      = 0x2F
DEACTIVATE_SCROLL                    = 0x2E
SET_VERTICAL_SCROLL_AREA             = 0xA3
RIGHT_HORIZONTAL_SCROLL              = 0x26
LEFT_HORIZONTAL_SCROLL               = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL  = 0x2A

PIXEL_OFF = 0
PIXEL_ON = 1
PIXEL_INVERT = 2

# The I2C device id default. Mine are always set to 0x78 on the back
# which turns into 0x3c since divide by 2 for the id
DEVID = 0x3c

# I2C communication here is either <DEVID> <CTL_CMD> <command byte>
# or <DEVID> <CTL_DAT> <display buffer bytes> <> <> <> <>...
# These two values encode the Co (Continuation) bit as b7 and the
# D/C# (Data/Command Selection) bit as b6.
# mz-it really looks like 0 is right here and not 0x80. i think irrelevant since always one command per packet
CTL_CMD = 0  # 0x80
CTL_DAT = 0x40

class OledDisplay(object) :

  def __init__(self, is1306=True, height=64, external_vcc=False, i2c_devid=DEVID):
    self.external_vcc = external_vcc
    self.height       = height
    self.pages        = int(self.height / 8)
    self.columns      = 128
    self.isSSD1306    = is1306
    self.i2c = I2cHelper.I2cHelper(i2c_devid)
    self.devid = i2c_devid
    # used to reserve an extra byte in the image buffer
    self.offset = 1
    # I2C command buffer
    self.cbuffer = bytearray(2)
    self.cbuffer[0] = CTL_CMD
    # data buffer
    self.buffer = bytearray(self.offset + self.pages * self.columns)
    self.buffer[0] = CTL_DAT

  # initialize the display hardware registers
  def init_display(self):
    chargepump = 0x10 if self.external_vcc else 0x14
    precharge  = 0x22 if self.external_vcc else 0xf1
    multiplex  = 0x1f if self.height == 32 else 0x3f
    compins    = 0x02 if self.height == 32 else 0x12
    contrast   = 0x9f
    # again note CHARGEPUMP isn't really on the SH1106. w/e
    data = [DISPLAYOFF,
            SETDISPLAYCLOCKDIV, 0x80,
            SETMULTIPLEX, multiplex,
            SETDISPLAYOFFSET, 0x00,
            SETSTARTLINE | 0x00,
            CHARGEPUMP, chargepump,
            MEMORYMODE, 0x00,
            SEGREMAP | 0x1,
            COMSCANDEC,
            SETCOMPINS, compins,
            SETCONTRAST, contrast,
            SETPRECHARGE, precharge,
            SETVCOMDETECT, 0x40,
            DISPLAYALLON_RESUME,
            NORMALDISPLAY,
            DISPLAYON]
    for item in data:
      self.write_command(item)
    self.clear()
    self.display()

  def write_command(self, command_byte):
    self.cbuffer[1] = command_byte
    self.i2c.SendBuffer(self.cbuffer)

  def invert_display(self, invert):
    self.write_command(INVERTDISPLAY if invert else NORMALDISPLAY)

  # clear the display buffer
  def clear(self):
    for i in range(self.offset, len(self.buffer)) :
      self.buffer[i] = 0

  # show the display buffer on-screen
  def display(self) :
    if self.isSSD1306 :
      self._display_ssd1306()
    else :
      self._display_sh1106()

  # the SSD1306 can take the data in a gulp
  def _display_ssd1306(self):
    self.write_command(COLUMNADDR)
    self.write_command(0)
    self.write_command(self.columns - 1)
    self.write_command(PAGEADDR)
    self.write_command(0)
    self.write_command(self.pages - 1)
    self.i2c.SendBuffer(self.buffer)

  # the SH1106 needs the data sent in per page
  def _display_sh1106(self):
    m_col = 2
    for y in range(0, self.pages) :
      self.write_command(SETPAGEADDR + y) # set page address
      self.write_command(SETCOLADDR_LOW | (m_col & 0xf)) # reset lower column address
      self.write_command(SETCOLADDR_HIGH | (m_col >> 4)) # reset higher column 
      # offset in the buffer
      dx = self.offset + y * self.columns
      # start with a data flag
      self.i2c.SendBuffer( bytearray([CTL_DAT]) + self.buffer[dx:dx + self.columns])

  # set/clear/invert a pixel at an (x,y) location. (0,0) = upper left
  def set_pixel(self, x, y, state):
    index = x + (int(y / 8) * self.columns)
    if state == PIXEL_OFF:
      self.buffer[self.offset+index] &= ~(1 << (y & 7))
    elif state == PIXEL_INVERT:
      self.buffer[self.offset+index] &= ~(1 << (y & 7))
    else : # state == PIXEL_ON
      self.buffer[self.offset+index] |= (1 << (y & 7))

  def poweron(self):
    self.write_command(DISPLAYON)

  def poweroff(self):
    self.write_command(DISPLAYOFF)

  def contrast(self, contrast):
    self.write_command(SETCONTRAST)
    self.write_command(contrast)
