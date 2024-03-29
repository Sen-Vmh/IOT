import threading
import wiringpi
import time
import smbus2
import bmp280
import requests
from smbus2 import SMBus, i2c_msg

# Define your functions here

def alerting_led_for_temp():
    global temperature, temp_threshold, green_led, orange_led, red_led
    if temp_threshold * 0.8 <= temperature <= temp_threshold * 1.2:
        wiringpi.digitalWrite(green_led, 1)  # Green LED on
        wiringpi.digitalWrite(orange_led, 0)  # Orange LED off
        wiringpi.digitalWrite(red_led, 0)  # Red LED off
    elif temp_threshold * 0.6 <= temperature <= temp_threshold * 1.4:
        wiringpi.digitalWrite(green_led, 0)  # Green LED off
        wiringpi.digitalWrite(orange_led, 1)  # Orange LED on
        wiringpi.digitalWrite(red_led, 0)  # Red LED off
    else:
        wiringpi.digitalWrite(green_led, 0)  # Green LED off
        wiringpi.digitalWrite(orange_led, 0)  # Orange LED off
        wiringpi.digitalWrite(red_led, 1)  # Red LED on
    
def ActivateADC():
    wiringpi.digitalWrite(pin_CS_adc, 0) # Activated ADC using CS
    time.sleep(0.000005)

def DeactivateADC():
    wiringpi.digitalWrite(pin_CS_adc, 1) # Deactivated ADC using CS
    time.sleep(0.000005)

def read_temperature_threshold(adc_number):
    if ((adc_number > 7) or (adc_number < 0)):
        return -1
    revlen, recvData = wiringpi.wiringPiSPIDataRW(1, bytes([1,(8+adc_number)<<4,0]))
    time.sleep(0.000005)
    adc_output = ((recvData[1]&3) << 8) + recvData[2]
    return(adc_output)

def read_lux_threshold(adc_number):
    if ((adc_number > 7) or (adc_number < 0)):
        return -1
    revlen, recvData = wiringpi.wiringPiSPIDataRW(1, bytes([1,(8+adc_number)<<4,0]))
    time.sleep(0.000005)
    adc_output = ((recvData[1]&3) << 8) + recvData[2]
    return(adc_output)

def sensor_reading_task():
    global lux_threshold, temp_threshold
    while True:
        if wiringpi.digitalRead(button_pin) == 0:
            # Button is held down, read sensor data
            ActivateADC()
            lux_threshold = read_lux_threshold(0) // 20
            DeactivateADC()
            ActivateADC()
            temp_threshold = read_temperature_threshold(1) // 33
            DeactivateADC()
        else:
            # Button is not held down, sleep for a short duration to reduce CPU usage
            time.sleep(0.1)

def button_polling_task():
    global count
    while True:
        # Poll button state and perform actions
        while wiringpi.digitalRead(button_pin) == 0:
            time.sleep(0.1)

def get_value(BMP280_bus, BMP280address):
    write = i2c_msg.write(BMP280_address, [0x10])
    read = i2c_msg.read(BMP280_address, 2)
    BMP280_bus.i2c_rdwr(write, read)
    bytes_read = list(read)
    return (((bytes_read[0]&3)<<8) + bytes_read[1])/1.2

def post_thingspeak():
    while True:
        requests.post(field2 +str(lux))
        time.sleep(15)
        requests.post(field1 +str(temperature))
        time.sleep(15)
        requests.post(field3 +str(lux_threshold))
        time.sleep(15)
        requests.post(field4 +str(temp_threshold))
        time.sleep(15)


# Setup and main code here
            
#thingspeak

field1 = 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field1='
field2 = 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field2='
field3= 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field3='
field4 = 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field4='

# BH1750

BH1750_bus = smbus2.SMBus(0) 
BH1750_address = 0x77

# BMP280

BMP280_bus = SMBus(0) # Use bus 1 for I2C communication on most Orange Pi models
BMP280_address = 0x23  # BMP280 default I2C address

# Initialize BMP280 sensor
bmp_sensor = bmp280.BMP280(i2c_dev=BH1750_bus, i2c_addr=BH1750_address)

if __name__ == "__main__":
    pin_CS_adc = 16  # We will use w16 as CE, not the default pin w15!
    button_pin = 3
    pwn_led = 4
    red_led = 5
    orange_led = 13
    green_led = 8
    count = 0
    lux_threshold = 50
    temp_threshold = 20
    temperature = 15
    lux = 500

    wiringpi.wiringPiSetup()
    wiringpi.pinMode(pin_CS_adc, 1)  # Set ce to mode 1 (OUTPUT)
    wiringpi.pinMode(button_pin, 0)
    wiringpi.pullUpDnControl(button_pin, wiringpi.PUD_UP)  # Enable pull-up resistor
    wiringpi.wiringPiSPISetupMode(1, 0, 500000, 0)  # (channel, port, speed, mode)
    wiringpi.pinMode(green_led, 1)       # Set pin 6 to 1 ( OUTPUT )
    wiringpi.pinMode(orange_led, 1)       # Set pin 6 to 1 ( OUTPUT )
    wiringpi.pinMode(red_led, 1)       # Set pin 6 to 1 ( OUTPUT )
    

    # Create and start sensor reading thread
    sensor_thread = threading.Thread(target=sensor_reading_task)
    sensor_thread.daemon = True  # Daemonize the thread to terminate with main thread
    sensor_thread.start()

    # Create and start button polling thread
    button_thread = threading.Thread(target=button_polling_task)
    button_thread.daemon = True  # Daemonize the thread to terminate with main thread
    button_thread.start()

    thingspeak_thread = threading.Thread(target=post_thingspeak)
    thingspeak_thread.daemon = True  # Daemonize the thread to terminate with main thread
    thingspeak_thread.start()

    BH1750_bus.write_byte(BH1750_address, 0x10)
    bytes_read = bytearray(2)

    

    try:
        while True:
            lux = get_value(BMP280_bus, BMP280_address)
            temperature = bmp_sensor.get_temperature()
            alerting_led_for_temp()
            print(f"lux = {round(lux, 2)} // Threshold = {lux_threshold}\ntemp = {round(temperature, 2)} // Threshold = {temp_threshold}\n")
            time.sleep(0.5)

    except KeyboardInterrupt:
        DeactivateADC()
        wiringpi.digitalWrite(green_led, 0)
        wiringpi.digitalWrite(orange_led, 0)
        wiringpi.digitalWrite(red_led, 0)
        wiringpi.digitalWrite(9 , 0)
        print("\nProgram terminated")


