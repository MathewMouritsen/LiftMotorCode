#!/usr/bin/env python3

#this program just goes through the various inclines and makes a table for you

import serial
import time
import binascii
import sb_lib
#import readline
import os
import sys



#===============main=====================
if os.name == 'nt':
    p = 'COM'
    i = '1'
else:
    p = '/dev/ttyUSB'
    i = '0' 
if(len(sys.argv) > 1):
    i = str(sys.argv[1])
p += i

#open output file to log results
with open("log.txt", 'w') as f:

    #open port 
    ser = serial.Serial(
        port=p,
        baudrate=38400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )

    ser.isOpen();#just a safety check
    numOfLifeCycles = 0
    sb_lib.welcome()
    sb_lib.printMenu()


    #a = [int(s) for s in st.replace(',',' ').split() if s.isdigit()]
    st = ""
    while st != 'q':
        print()
        st = input("Next message (m for menu, q to quit): ")
        if(st and st != 'q'):
            if(st == 'm'):
                sb_lib.printMenu()
                continue
            if(st == "1"): # calibrate incline 
                print("calibrating incline")
                st = "41 03 00"
                m = bytearray(b"")
                m = sb_lib.sendMsg(ser,st)
            if(st == "2"): # send incline to 'safe' top 
                sb_lib.goToTop(ser)
                print("sending incline to top")
            if(st == "3"): # send incline to 'safe' bottom
                sb_lib.goToBottom(ser)
                print("sending incline to bottom")
            if (st == "4"): ##incline life test
                print("typical life tests need 10,000 cycles to pass")
                needCycles = int(input("please enter how many cycles you want-> "))
                print()
                sb_lib.inclineLifeTest(ser,needCycles,f)
            if (st == "5"):
                m =  sb_lib.readIncline(ser)
                print("incline is at ", m,"half-percentages above the bottome limit (-6% is the bottom limit in this case)")
                print()
            if (st == '6'):
                sb_lib.goToZero(ser)
                print("sending incline to zero")
            if (st == "7"):
                response = input("where would you like the incline to go to? -> ")
                sb_lib.goTo(ser,response)
                print("sending incline to ", response)
            if (st == "9"):
                sb_lib.nineCycleTest(ser)
            if(st == "8"):
                print("test not yet implemented")
                ##TODO this will be the temp stabalization test
            if(st == "10"):
                print()
                print("updating rise time")
                riseTime = sb_lib.updateRise(ser)
            if(st == "11"):
                print()
                print("updating fall time")
                fallTime = sb_lib.updateFall(ser)
           # if(len(m)):
                #sb_lib.printSBdata(m)


    ser.close();

    print("fwhew! Is that all?")



