from graphicslib import pighelp
import time
import pigpio
import math

# this code was taken from the Adafruit_PWM_Servo_Driver
# a small bug was fixed for full on
# and it was modified to use pigpio and print

class PwmDevice():
        # Registers/etc.
    __MODE1              = 0x00
    __MODE2              = 0x01
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALL_LED_ON_L       = 0xFA
    __ALL_LED_ON_H       = 0xFB
    __ALL_LED_OFF_L      = 0xFC
    __ALL_LED_OFF_H      = 0xFD

    # Bits
    __RESTART            = 0x80
    __SLEEP              = 0x10
    __ALLCALL            = 0x01
    __OUTDRV             = 0x04

    def __init__(self):
        self.i2c = pighelp.PIGHELPER.geti2cPwm()
        self.setAllPWM(0, 0)
        self.write8(self.__MODE2, self.__OUTDRV)
        self.write8(self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)                             # wait for oscillator
        mode1 = self.readU8(self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
        self.write8(self.__MODE1, mode1)
        time.sleep(0.005)
        self.setPWMFreq(1000)   # default permanently to 1KHz for fan motor

    def write8(self, register, value) :
        ''' encapsulating the i2c write request '''
        pighelp.PIGHELPER.Api.i2c_write_byte_data(self.i2c, register, value)

    def readU8(self, register) :
        ''' encapsulating the i2c read request '''
        return pighelp.PIGHELPER.Api.i2c_read_byte_data(self.i2c, register)

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        print("Setting PWM frequency to %d Hz" % freq)
        print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        print("Final pre-scale: %d" % prescale)
        oldmode = self.readU8(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10             # sleep
        self.write8(self.__MODE1, newmode)        # go to sleep
        self.write8(self.__PRESCALE, int(math.floor(prescale)))
        self.write8(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write8(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel. Note that there's a special bit at H (8) for full on"
        self.write8(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write8(self.__LED0_ON_H+4*channel, on >> 8)
        self.write8(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write8(self.__LED0_OFF_H+4*channel, off >> 8)

    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.write8(self.__ALL_LED_ON_L, on & 0xFF)
        self.write8(self.__ALL_LED_ON_H, on >> 8)
        self.write8(self.__ALL_LED_OFF_L, off & 0xFF)
        self.write8(self.__ALL_LED_OFF_H, off >> 8)

class PwmControl():
    ''' a pwm controller, set the device to pwmdevice instance and channel to 0...3 '''
    def __init__(self, device, channel):
        self.channel = channel
        self.device = device
        pwm = in1 = in2 = 0
        if (channel == 0):
            pwm = 8
            in2 = 9
            in1 = 10
        elif (channel == 1):
            pwm = 13
            in2 = 12
            in1 = 11
        elif (channel == 2):
            pwm = 2
            in2 = 3
            in1 = 4
        elif (channel == 3):
            pwm = 7
            in2 = 6
            in1 = 5
        else:
            raise NameError('Pwm Channel must be between 0 and 3 inclusive')
        self.PWMpin = pwm
        self.IN1pin = in1
        self.IN2pin = in2
        self.setPolarity(0) # permanently set as a DC supply with + on the left
        self.setSpeed(0) # and default to turn off

    def setPin(self, pin, value):
        ''' set a pin on or off. there's a special bit in the register at 4096 for on/off '''
        if (value == 0):
            self.device.setPWM(pin, 0, 4096)
        elif (value == 1):
            self.device.setPWM(pin, 4096, 0)

    def setPolarity(self, command):
        ''' set the output polarity '''
        if (command == 0): # +-
            self.setPin(self.IN2pin, 0)
            self.setPin(self.IN1pin, 1)
        elif (command == 1): # -+
            self.setPin(self.IN1pin, 0)
            self.setPin(self.IN2pin, 1)
        elif (command == 2): # 00
            self.setPin(self.IN1pin, 0)
            self.setPin(self.IN2pin, 0)

    def setSpeed(self, speed):
        ''' set the pwm on/off values, i.e. speed in range [0...100] '''
        if (speed < 0):
            speed = 0
        elif (speed > 100):
            speed = 100
            ''' the on time is how long before turning on the device. this should always be zero
                the off time is how long before turning off. this should be 0...4095 with 4095 == always on
                but there's a special bit for 4096 that is all on
            '''
        if speed > 0 and speed < 100:
            self.device.setPWM(self.PWMpin, 0, speed * 41)
        else:
            self.setPin(self.PWMpin, 1 if speed > 0 else 0)
