import time
import wiringpi
import sys

def blink(_pin):
    wiringpi.digitalWrite(_pin, 1)
    time.sleep(0.5)
    wiringpi.digitalWrite(_pin, 0)
    time.sleep(0.5)

#setup 
print("start")
pin = [2,3,4,6]


wiringpi.wiringPiSetup()
for i in pin:
    wiringpi.pinMode(i, 1)

#main
try:
    while True:
        blink(pin[0])


except KeyboardInterrupt:
    for i in pin:
        wiringpi.digitalWrite(i, 0)
#cleanup
print("done")


