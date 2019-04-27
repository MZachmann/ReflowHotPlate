# this code simply initializes I2C (only once)
# and is a wrapper for comm with a single I2C address
# from machine import I2C
from graphicslib import pighelp

I2CInitialized = False # true when we've done that
BaseI2c = None # put the first created one here to clone the i2c

class I2cHelper(object) :
    def __init__(self, addr) :
        global I2CInitialized
        global BaseI2c
        try :
            # only initialize this once
            if not I2CInitialized :
                I2CInitialized = True
                self.addr = addr
                self.i2c = pighelp.PIGHELPER.geti2cDisplay() # open device at address 0x53 on bus 1
                #I2C(0, I2C.MASTER, sda=23, scl=22, freq=400000)
                BaseI2c = self.i2c # the clone source
            else:
                self.addr = addr
                self.i2c = BaseI2c
        except Exception as e :
            print( 'Er0:' + str(e))
            self.i2c = None
            self.addr = 0

    # send a bytearray (value) via i2c
    def SendBuffer(self, value) :
        work = False
        if self.i2c :
            try :
                #rslt = self.i2c.writeto(self.addr, value)
                rslt = pighelp.PIGHELPER.Api.i2c_write_device(self.i2c, value)
                work = (rslt == len(value))
            except Exception as ex :
                print( 'Er1:' + str(ex))
        else :
            print('No i2c available.')
        return work

    # send a string (value) via i2c
    def SendString(self, value) :
        return self.SendBuffer(bytearray(value))

    # read (size) bytes from i2c
    def ReadBuffer(self, size) :
        bx = None
        count = -1
        if self.i2c :
            try :
                (count, bx) = pighelp.PIGHELPER.Api.i2c.read_device(self.i2c, size)
            except Exception as e :
                print( 'Er2:' + str(e))
        else :
            print('No i2c available.')
        if count < 0 :
            print('No data returned.')
        return bx

    # read a string of length (size) from i2c
    def ReadString(self, size) :
        vout = None
        bf = self.ReadBuffer(size)
        if bf :
            vout = bf.encode('UTF-8')
        return vout

