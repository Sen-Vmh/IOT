import time
import wiringpi
import sys

def pwm_led(pin_pwm, value):
    wiringpi.softPwmWrite(pin_pwm, value)

pin_pwm = 4

wiringpi.wiringPiSetup()

wiringpi.softPwmCreate(pin_pwm, 0, 300)

try:
    while True:
        # Increase brightness
        for i in range(0, 301):
            pwm_led(pin_pwm, i)
            time.sleep(0.02)  # Adjust the sleep duration for speed
        # Decrease brightness
        for i in range(100, -1, -1):
            pwm_led(pin_pwm, i)
            time.sleep(0.02)  # Adjust the sleep duration for speed
            if i == 0:
                break  # Break the loop if brightness is reduced to 0

except KeyboardInterrupt:
    wiringpi.softPwmWrite(pin_pwm, 301)
    wiringpi.digitalWrite(pin_pwm, 0)  # Turn off the pin explicitly
    wiringpi.digitalWrite(pin_pwm, 0)
    print("finito")
