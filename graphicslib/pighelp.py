import pigpio

class PigHelp():
    def __init__(self):
        try:
            self.Api = pigpio.pi()
            self.hspi = self.Api.spi_open(0, 1000000, 0) # temperature
            self.i2cDisplay = self.Api.i2c_open(1, 0x3c) # oled
            self.i2cPwm = self.Api.i2c_open(1, 0x60) # pwm device
        except Exception as ex:
            print("Error: " + str(ex))

    def getspi(self):
        return self.hspi

    def geti2cDisplay(self):
        return self.i2cDisplay

    def geti2cPwm(self):
        return self.i2cPwm

PIGHELPER = PigHelp()
