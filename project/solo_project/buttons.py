import wiringpi
import time
import sys

print("start")

min = 3
count = 0

wiringpi.wiringPiSetup()
wiringpi.pinMode(min, 0)
wiringpi.pullUpDnControl(min, wiringpi.PUD_UP)  # Enable pull-up resistor

while True:
    if wiringpi.digitalRead(min) == 0:  # Button is pressed when the input is LOW (0)
        count -= 1
        print(count)
    time.sleep(0.1)
