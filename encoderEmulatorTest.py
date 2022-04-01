import RPi.GPIO as GPIO
import time

mostRecent = "0"

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(16, GPIO.LOW)
    GPIO.output(12, GPIO.LOW)

    while True:
        response = input("(U)p, (D)own, or (F)inish?")
        if response == "u" or response == "U":
            up()
        elif response == "d" or response == "D":
            down()
        elif response == "f" or response == "F":
            GPIO.cleanup()
            return

def down():
    global mostRecent
    times = 4 if mostRecent == "up" else 2
    for i in range(times):
        downHelper()
        mostRecent = "down"
    return

def downHelper():
    GPIO.output(12, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(12, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(16, GPIO.LOW)
    time.sleep(0.25)

def up():
    global mostRecent
    times = 4 if mostRecent == "down" else 2
    for i in range(times):
        upHelper()
    mostRecent = "up"
    return

def upHelper():
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(12, GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(16, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(12, GPIO.LOW)
    time.sleep(0.25)
    return

main()
    