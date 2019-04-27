from graphicslib import OledGrafx, pighelp
import pwmcontrol
import time
import _thread
import pigpio
import threading
import queue

HOTBIT = 18 # the pin with the switch
FANBIT = 23 # the pin for the fan

# hspi = SPI(1, baudrate=1000000, polarity=0, phase=0)

isRunning = True
iamRunning = False
runLoop = True

PwmObject = pwmcontrol.PwmDevice()
FanMotor = pwmcontrol.PwmControl(PwmObject, 0)
VoltagePin = pwmcontrol.PwmControl(PwmObject, 2)

def getApi():
    ''' get the io controller '''
    return pighelp.PIGHELPER.Api

def setVoltage(amt):
    ''' Set the heat button on/off. amt=boolean '''
    VoltagePin.setSpeed(100 if amt else 0)

def getSpi():
    ''' get the spi controller '''
    return pighelp.PIGHELPER.getspi()

def readSpi(hspi):
    ''' read the spi data. This gets temperature/reference packed '''
    (ct, data) = getApi().spi_read(hspi, 4)
    return data

def dataToTemp(data):
    ''' convert raw spi output into temperature data '''
    # sign, 13 bits of data (*4), res, 1 bit fault=1,
    # sign, 10 bits (*16) internal, res, 3 fault bits
    # int is four bytes, so... '''
    temp = int.from_bytes(data[0:2], 'big') >> 2 # 14 bits of data
    temp = temp / 4.0   # a few decimal places
    ref = int.from_bytes(data[2:4], 'big') >> 4  # 12 bits of data
    ref = ref / 16.0
    return temp, ref

def setFanRate(rate):
    FanMotor.setSpeed(rate)

class TempRunner(threading.Thread):
    ''' threaded pwm temperature switching '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.que = queue.Queue(20)
        self.percent = 0
        self.cycletime = 1
        self.running = True

    def run(self):
        ''' overriden, call start() to run this thread '''
        setVoltage(0)
        try:
            ton = self.percent * self.cycletime / 100.0
            toff = (100-self.percent) * self.cycletime / 100.0
            while self.running:
                if not self.que.empty():
                    (self.percent, self.cycletime) = self.que.get()
                    ton = self.percent * self.cycletime / 100.0
                    toff = (100-self.percent) * self.cycletime / 100.0
                    setVoltage(0)
                if self.percent > 0:
                    setVoltage(1)
                    time.sleep(ton)
                    if self.percent < 100:
                        setVoltage(0)
                        time.sleep(toff)
                else:
                    # no percent so just keep sleeping
                    time.sleep(.2)
        except Exception as ex:
            print("doPwmTemp error: " + str(ex))
        setVoltage(0)

    def stop(self):
        ''' asynchronous stop '''
        self.running = False

    def setCycle(self, percent, cycletime):
        # this automatically changes the cycle time and percent
        self.que.put((percent, cycletime))

class Reader():
    def __init__(self):
        # turn off the voltage just in case
        getApi().set_mode(HOTBIT, pigpio.OUTPUT)
        setVoltage(0)
        #
        self.oled = OledGrafx.OledGrafx(False)
        self.oled.PrintStrings("Initial","Setup","","")
        self.hspi = getSpi()
        self.rque = queue.Queue(20)
        self.starttime = time.time()

    def readvalue(self):
        #data=bytearray(4)
        Api = pighelp.PIGHELPER.Api
        (ct, data) = Api.spi_read(self.hspi, 4)
        #self.hspi.readinto(data)
        return data

    def Stop(self):
        global isRunning
        isRunning = False

    def enableV(self):
        self.oled.PrintStrings("Initial","Setup","","")

    def printread(self):
        data = self.readvalue()
        temp,ref = dataToTemp(data)

    def printpos(self, posn, temper):
        if posn == 0:
                self.oled.PrintStrings(first=str(temper))
        elif posn == 1:
                self.oled.PrintStrings(second=str(temper))
        elif posn == 2:
                self.oled.PrintStrings(third=str(temper))
        else:
                self.oled.PrintStrings(fourth=str(temper))

    def rloop(self, target=0, limit=0, keeptime=False):
        position = 0
        runLoop = True
        begintime = time.time()
        if keeptime:
            started = self.starttime
        else:
            started = begintime
        while runLoop:
            time.sleep(.1)
            data = self.readvalue()
            temp,_ = dataToTemp(data)
            temp = 32 + temp * 9 /5
            # stop when we hit temperature target
            if target > 0 and temp >= target:
                print("At target temperature.")
                runLoop = False
            now = time.time()
            if limit > 0 and (now-begintime) > limit:
                print("At target time.")
                runLoop = False
            position = position + 1
            if not (position % 10):
                self.printpos( (position/10) % 4, temp)
                print("{0:.2f} ::: ".format(now-started) + str(temp))

    def doset(self, temper):
        position = 0
        ison = True
        setValue(0)
        while runLoop:
            data = self.readvalue()
            temp,_ = dataToTemp(data)
            temp = 32 + temp * 9 /5
            self.printpos( position, temp)
            if ison and temp > (temper-2):
                ison = False
                setValue(0)
            elif not ison and temp < (temper-5):
                setValue(1)
                ison = True
            time.sleep(1)
            position = position + 1
            if position == 4:
                position = 0
            now = time.gmtime() # hours, minutes, seconds
            print("At {}:{}.{} ::: ".format(now[3], now[4], now[5]) + str(temp))
        setValue(0)

    def dotest(self, percent, rate):
        global isRunning
        isRunning = False
        time.sleep(.1)
        isRunning = True
        position = 0
        ison = True
        print("start thread")
        tid = _thread.start_new_thread(doPwmTemp, (percent,rate))
        print("thread going")
        starttime = time.time()
        while isRunning and runLoop:
            data = self.readvalue()
            temp,_ = dataToTemp(data)
            temp = 32 + temp * 9 /5
            self.printpos( position % 4, temp)
            position = position + 1
            now = time.time() - starttime # elapsed seconds since start
            if 0 == (position % 10):
                print("At {} ::: ".format(now) + str(temp))


def runScript():
    trun = TempRunner()
    rdr = Reader()   # wait for 220F
    trun.setCycle(0, 1) # turn it off for now
    trun.start()
    trun.setCycle(100, 1) # full on
    rdr.rloop(target=220, keeptime=True)
    trun.setCycle(25, 1) # slow
    rdr.rloop(target=300, keeptime=True)
    trun.setCycle(100, 1)
    rdr.rloop(target=385, keeptime=True) # we need 20C > melting point
    trun.setCycle(0, 1) # turn off stuff
    # time to turn on the fan...
    setFanRate(50) # run half speed for a bit
    rdr.rloop(limit=10, keeptime=True) # 10 seconds
    setFanRate(100) # run full speed to not get too hot
    rdr.rloop(limit=20, keeptime=True)
    setFanRate(35) # run quarter speed to keep liquid longer (lowest speed it rotates at)
    rdr.rloop(limit=45, keeptime=True)
    setFanRate(100) # run full speed to cool down
    rdr.rloop(limit=180, keeptime=True)
    setFanRate(0) # turn off the fan after 180 seconds
