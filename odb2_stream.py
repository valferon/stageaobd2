import time
import math
import threading
import datetime
from utils import *


class ReadStream(threading.Thread):

    def __init__(self, port,connected = False):
        self.port = port
        self.connected  = connected
        self.stream = False
        self.MPH_Value = 0
        self.RPM_Value = 0
        self.TEMP_Value = 0
        self.BATT_Value = 0
        self.MAF_Value = 0
        self.AAC_Value = 0
        self.INJ_Value = 0
        self.TIM_Value = 0
        self.fileName = datetime.datetime.now().strftime("%d-%m-%y-%H-%M")

        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def getElmInfo(self):
		try:
			self.port.write("ATI\r")
			data = self.port.readline()
			return data[:-1]
		except OSError:
			print RED + 'Command timed out!' + ENDC
			return -1

    def run(self):

        while self.connected == False:

            self.port.write('\xFF\xFF\xEF')
            time.sleep(2)
            isConnected = self.port.inWaiting()

            if isConnected:
                ecuResponse = self.port.read(1)
                if ecuResponse == '\x10':
                    print 'Correct reply from ECU, sending data...'
                    self.connected = True

                else:
                    print 'Wrong reply from ECU'

            else:
                print 'Trying to connect to ECU'
                self.port.write('\xFF\xFF\xEF')
                time.sleep(2)


        self.port.write('\x5A\x0B\x5A\x01\x5A\x08\x5A\x0C\x5A\x0D\x5A\x03\x5A\x05\x5A\x09\x5A\x13\x5A\x16\x5A\x17\x5A\x1A\x5A\x1C\x5A\x21\xF0')
        print 'waiting for ECU to stream data...'

        while self.stream == False:
            Header = 255
            returnBytes = 14
            frameStart = self.port.read(3)
            frameList = map(ord,frameStart)

            if frameList[1] == Header and frameList[2] == returnBytes:
                print 'Data stream aligned, streaming from ECU.'
                self.stream = True

            else:
                print 'Aligning data stream from ECU...'


        while self.stream == True:
            incomingData = self.port.read(16)

            '''uncomment to log incoming data to file
            '''
            #self.logToFile(incomingData,fileName)

            if incomingData:

                dataList = map(ord,incomingData)

                self.MPH_Value = self.convertToMPH(int(dataList[0]))
                self.RPM_Value = self.convertToRev(int(dataList[1]))
                self.TEMP_Value = self.convertToTemp(int(dataList[2]))
                self.BATT_Value = self.convertToBattery(float(dataList[3]))
                self.AAC_Value = self.convertToAAC(int(dataList[10]))
                self.MAF_Value = self.convertToMAF(int(dataList[7]))


            else:
                pass


    def convertToMPH(self,inputData):

        return int(round ((inputData * 2.11) * 0.621371192237334))

    def convertToRev(self,inputData):

        return int(round((inputData * 12.5),2))

    def convertToTemp(self,inputData):

        return inputData - 50

    def convertToBattery(self,inputData):

        return round(((inputData * 80) / 1000),1)

    def convertToMAF(self,inputData):

        return inputData * 5

    def convertToAAC(self,inputData):

        return inputData / 2

    def convertToInjection(self,inputData):

        return inputData / 100

    def convertToTiming(self,inputData):

        return 110 - inputData

    def logToFile(self,data,fileName):

        logFile = open(fileName + '.hex', 'a+')

        logFile.write(data)

    def returnMPH(self):
        return self.MPH_Value

    def returnRPM(self):
        return self.RPM_Value

    def returnTEMP(self):
        return self.TEMP_Value

    def returnBATT(self):
        return self.BATT_Value

    def returnAAC(self):
        return self.AAC_Value

    def returnMAF(self):
        return self.MAF_Value
