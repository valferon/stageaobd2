import os
import sys
import serial
from odb2_stream import *
from utils import *

def main():
    interface = '/dev/pts/23'
    print PINK + 'Opening serial connection on ' + BLUE + interface + ENDC
    
    PORT = serial.Serial(interface, 9600, timeout=None)
    incomingData = ReadStream(PORT,False)
    
    print 'Adaptor info :' + incomingData.getElmInfo()

if __name__ == "__main__":
    main()
