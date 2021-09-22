#JJHHHJJi!/usr/bin/env python3

#this is just a bunch of helper functions 

import serial
import time
import binascii
#import readline
from itertools import islice
import os

if os.name == 'nt':
    class bcolors:
        HEADER = ''
        OKBLUE = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
else:
    class bcolors:
        HEADER = '\033[35m'
        OKBLUE = '\033[34m'
        OKGREEN = '\033[32m'
        WARNING = '\033[33m'
        FAIL = '\033[31m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

# here is the lrc stuff
def calcLRC(msg):
    lrc = 0
    for i in range(0,len(msg),2):
        lrc += int(msg[i:i+2],16)#int(chr(b),16)
        lrc &= 0xff
    lrc = (~(lrc -1))&0xff
    return lrc
    
def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

# and the shortbus stuff 


def sbify(addr, cmd, arg):
    addr = bytearray(addr,"utf-8")
    cmd = bytearray(cmd,"utf-8")
    #:aaddccccxxxx CRC \r\n
    if addr[0] != b':':
        addr = b':' + addr
    if len(arg):
        addr += b'06' # since we have data we assume its a write
    elif len(addr)<5:
        addr += b'03'
    if len(addr)<6: 
        addr += cmd.rjust(4,b'0')
    if ("0x" in arg):
        addr += bytearray(hex(int(arg,16))[2:].rjust(4,"0"),"utf-8")
    elif len(arg):
        addr += bytearray(hex(int(arg))[2:].rjust(4,"0"),"utf-8")
    else:
        addr += b'0000'
    #print(calcLRC(addr[1:]))
    addr += bytearray(hex(calcLRC(addr[1:]))[2:].rjust(2,"0"),"utf-8")
    addr += bytearray("\r\n","utf-8")
    addr = addr.upper()
    return addr
   
def sbifyst(st):
    if(len(st.split())>2):
        return sbify(st.split()[0],st.split()[1],st.split()[2])
    elif(len(st.split())>1): 
        return sbify(st.split()[0],st.split()[1],"")
    else:
        return sbify(st,"","")


# returns data value from complete message
def getSBdata(msg):
    #msg = bytearray(msg)
    #l = len(msg)
    #x = findmsgXsum(msg,l-1)
    if(isreply(msg)):
        i = msg.find(b':')+11
    else:
        i = msg.find(b':')+9
    j = msg.find(b'\r')-2
    return int(msg[i:j],16)

#this will break up multibyte data into the values
def printSBdata(msg):
    if(isreply(msg)):
        i = msg.find(b':')+11
        l = int(msg[i-6:i-4],16)
    else:
        i = msg.find(b':')+9
        l = 2
    j = msg.find(b'\r')-2
    if(i<9 or j == -1):
        return
    if l <= 2:
        v = int(msg[i:i+l*2],16)
    else:
        v = int(msg[i:i+4],16)
    print("\n returned: ",v," (", hex(v),")")
    for k in range(4,j-i,4):
        v = int(msg[i+k:i+k+4],16)
        print("           ",v," (", hex(v),")")

#this makes a tuple from a multiple byte data packet
def breakupSBdata(msg):
    if(isreply(msg)):
        i = msg.find(b':')+11
    else:
        i = msg.find(b':')+9
    j = msg.find(b'\r')-2
    if(i<9 or j == -1):
        return
    v = (int(msg[i:i+4],16),)
    for k in range(4,j-i,4):
        v += ( int(msg[i+k:i+k+4],16),)
    return v
        

# here we know that it's a complete message this pretty prints it
def show(msg):
    print()
    print("%.3f" % time.time(), end=" ")
    i = msg.find(b'\r')
    if(i == -1):
        #it wasn't a complete message
        print(msg)
        return
    print(msg[0:3].decode('utf-8'), end="")
    if(msg[4] == 51): #
        #get
        print(bcolors.OKGREEN + msg[3:5].decode('utf-8') + bcolors.ENDC, end="")
    else:
        #set
        print(bcolors.OKBLUE + msg[3:5].decode('utf-8') + bcolors.ENDC, end="")

    j = i-2
    if(isreply(msg)):
        i = 11#msg.find(b':')+11
    else:
        i = 9#msg.find(b':')+9

    print(msg[5:i].decode('utf-8'), end=" ")
    print(msg[i:j].decode('utf-8'), end=" ")
    print(msg[j:j+2].decode('utf-8'), end="")
    #print("0x%2s 0x%2s" %(binascii.hexlify(msg[4:6]).decode('utf-8'), binascii.hexlify(msg[6:8]).decode('utf-8') ), end=" ")


def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

# find index of first byte in xsum, assumes complete message
#def findmsgXsum(msg):
#    x = len(msg)-2;
#    if(msg[x] == 0xf7):
#        x -= 1 
#    if(msg[x-1] == 0xf7):
#        x -= 1
#    return x

# this assumes the first byte is the start char ':'
def isreply(msg):
    #if(findmsgEnd(msg) > 15):
    if msg[6] != 48: #check for reserved byte or length
        return True
    return False



# finds the length to end of the message or the byte before the next begins (if cutoff), this assumes the first byte is the start of a message
def findmsgEnd(msg):
    i = msg.find(b'\r')
    if i==-1:
        msg.find(b':')
    if i==-1:
        return 0
    return i

# finds start of next message in a buffer of messages
def findmsg(msg,ignore):
    n = 0;
    r = iter(range(len(msg)))
    for i in r:
        b = msg[i];
        if b == 58:
            j = findmsgEnd(msg[i:])
            if(j == 0):
                # don't have complete message yet, wait
                return i;
            if(n):
                 #newline for start characters if they are in the middle of the message
                print("") 
                print("%.3f" % time.time(), end=" ")
            #show(msg[i:]) 
#disable comm timeout
            i += j
            consume(r,j)
        elif not ignore:
            # print partial or bad message
            if not n:
                print()
                print("%.3f" % time.time(), end=" ")
            print(chr(b), end="")
            n = 1
    return i+1

# this simplified function adds delay to give time for the message to come through
# for more control use recieve and showmsg separately
def getReply(ser):
    time.sleep(.1)
    out = recieve(ser)
    if(out):
        findmsg(out, True) #2nd arg is ignore
    return out

# this grabs the data from the serial RX and returns it
def recieve(ser):
    time.sleep(.01)
    out = bytearray(b"")
    while ser.inWaiting() > 0:
        n = ser.inWaiting()
        out += ser.read(n)
    return out

# this sends and shows the sent message
def send(ser,m):
    ser.write(m)

#this function allows you to use it like you would the sb_terminal
def sendMsg(ser,st):
    m = sbifyst(st)
    send(ser,m)
    #show(m)
    return getReply(ser) 

##################################################################################################################
#################################ADDITIONS MADE BY DANIEL MORTENSON###############################################
#################################TODO MOVE TO A SEPERATE INCLINE SPECIFIC FILE####################################
##################################################################################################################
##################################################################################################################
#go to top (should be fairly self explanitory
def goToTop(ser):
    sendMsg(ser, "41 1 90")
    return
##go to bottom (purpose shold also be self explanitory)
def goToBottom(ser):
    sendMsg(ser, "41 1 2")
    return
## read current incline
##grabs the bytearray from kiwi and translates it into a hight as an integer
## TODO ask Jaron how he would like height displayed, it is currently in half percentages where 0 = bottom limit
## returns incline as an integer
def readIncline(ser):
    m = sendMsg(ser, "41 02")
    rando = ""
    rando = chr(m[13]) + chr(m[14])
    return int(rando, 16)

##incline life cycle test
##50% duty cycle assumed (motor is moving 50% of the time and resting the other 50%)
## verify's that the incline makes it to it's goal
## returns number of cycles completed as an integer
def inclineLifeTest(ser,needCycles,f):
    i = 0
    print("setting start conditions")
    print("updating rise time")
    riseTime = updateRise(ser)
    print("riseTime updated to ",riseTime)
    print("resting...")
    time.sleep(riseTime)

    print("updating fall time")
    fallTime = updateFall(ser)
    print("fallTime updated to: ",fallTime)
    print("resting...")
    time.sleep(fallTime)

    i = i+1
    print (bcolors.OKBLUE + str(i) + bcolors.ENDC + " Cycle completed")
    
    while i < needCycles:
        goToTop(ser)
        print("moving up...") 
        time.sleep(riseTime)
        print("resting...")
        time.sleep(riseTime)
        print("verifying...")
        if(readIncline(ser) == 92):
            print(bcolors.FAIL + "incline has failed to rise")
            print(i," Cycles completed before issue" + bcolors.ENDC)
            print("incline has failed to rise\n", i, " cycles completed before failure", file=f)
            return i
        goToBottom(ser)
        print("moving down...")
        time.sleep(fallTime)
        print("resting...")
        time.sleep(fallTime)
        print("verifying...")
        if(readIncline(ser) == 0):
            print(bcolors.FAIL + "incline has failed to lower")
            print(i, " Cycles completed before issue" + bcolors.ENDC)
            print("incline has failed to lower\n", i, " cycles completed before failure", file=f)
            return i
        i=i+1
        print(bcolors.OKBLUE + str(i) + " cycles completed" + bcolors.ENDC)
        if(i % 10 == 0):
            print (i, " Cycles completed ",file=f)
    print(bcolors.OKGREEN + str(i) + " cycles completed in this test")
    print(i, " cycles completed in this test", file=f)
    print("no issues found" +  bcolors.ENDC )
    goToZero(ser)
    return i


##prints the menu of options to the "daniels shortbus terminal"
def printMenu():
    print("")
    print(bcolors.UNDERLINE + bcolors.HEADER + "menu" + bcolors.ENDC)
    print(" 1 - calibrate incline")
    print(" 2 - send incline to 'safe' top")
    print(" 3 - send incline to 'safe' bottom")
    print(" 4 - incline life cycle test")
    print(" 5 - read current inlcine")
    print(" 6 - send incline to zero (flat)")
    print(" 7 - send incline to any specified height") 
    print(" 8 - temp stabalization test (coming soon)")
    print(" 9 - nine cycle test")
    print(" q - quit")
    
    return

## sends the incline to the 0%
def goToZero(ser):
     sendMsg(ser, "41 1 12")
     return

## sends incline to desired location based on user input
def goTo(ser, desiredIncline):
     st = "41 1 " + desiredIncline
     sendMsg(ser,st)
     return

## returns true if incline is at location being checked
def verifyIncline(ser, desiredIncline):
    if (desiredIncline == readIncline(ser)):
        return 1
    else:
        return 0
##has incline failed, return true if failed, false if not failed
def hasfailed(ser):
    if(verifyIncline(ser,92) or verifyIncline(ser,0)):
        return 1
    else:
        return 0

##Incline nineCycleTest
def nineCycleTest(ser):
    cycles = 0
    print("setting start conditions")
    goToZero(ser)
    time.sleep(25)
    for i in range(3):
        for j in range(3):
            goToTop(ser)
            time.sleep(5) # waiting for five seconds helps avoid an error
            while(not verifyIncline(ser,90)):
                if(hasfailed(ser)):
                    print(bcolors.FAIL + "Incline has failed on cycle " + str(cycles + 1) + bcolors.ENDC)
                    return

            goToBottom(ser)
            time.sleep(5) # waiting for five seconds helps to avoid an error
            while(not verifyIncline(ser,2)):
                if(hasfailed(ser)):
                    print(bcolors.FAIL + "incline has failed on cycle "+ str(cycles + 1) + bcolors.ENDC)
                    return
            cycles = cycles + 1
            print("cycle ", cycles, " completed")
        time.sleep(300) # wait 5 minutes (300 seconds)
    while(cycles > 0):
        goToTop(ser)
        time.sleep(5) # waiting for five seconds helps avoid an error
        while(not verifyIncline(ser,90)):
            if(hasfailed(ser)):
                print(bcolors.FAIL + "incline has failed on cycle "+ str(cycles + 1) + bcolors.ENDC)
                return

        goToBottom(ser)
        time.sleep(5) # waiting for five seconds helps to avoid an error
        while(not verifyIncline(ser,2)):
            if(hasfailed(ser)):
                print(bcolors.FAIL + "incline has failed on cycle "+ str(cycles + 1) + bcolors.ENDC)
                return
        cycles = cycles + 1
        print("cycle ", cycles, " completed")

##updates time taken to raise the motor
def updateRise(ser):
    goToBottom(ser)
    time.sleep(5)
    while(not verifyIncline(ser, 2)):
        if(hasfailed(ser)):
                print("incline has failed")
                return
    start = time.time()
    goToTop(ser)
    time.sleep(5)
    while(not verifyIncline(ser,90)):
        if(hasfailed(ser)):
            print('incline has failed')
            return
    riseTime = time.time() - start
    #print("riseTime updated to: ", riseTime, " seconds")
    return riseTime

def updateFall(ser):
    goToTop(ser)
    time.sleep(5)
    while(not verifyIncline(ser,90)):
        if(hasfailed(ser)):
            print("incline has failed")
            return
    start = time.time()
    goToBottom(ser)
    time.sleep(5)
    while(not verifyIncline(ser,2)):
        if(hasfailed(ser)):
            print("incline has failed")
            return
    fallTime = time.time() - start
    #print("fallTime updated to: ", fallTime, " seconds")

    return fallTime


##temp stabalization test
def tempStab(ser):
    print("test not yet implemented")
    ##############################################################################
    #this funciton will need to be able to perfrom a duty cycle of 50% without needing to prompt the user
    # but will need to stop when prompted by the user
    ##############################################################################

def welcome():
    print(bcolors.HEADER + bcolors.BOLD + "a benevolent welcome to the incline short-bus terminal 2.3.1", end=" ")
    print(bcolors.OKBLUE + "now " +  bcolors.WARNING + "in " + bcolors.OKGREEN + bcolors.UNDERLINE + "COLOR" + bcolors.ENDC)
