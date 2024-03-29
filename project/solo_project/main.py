import time
import smbus2
import bmp280
import requests
from smbus2 import SMBus, i2c_msg

#thingspeak

field1 = 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field1='
field2 = 'https://api.thingspeak.com/update?api_key=N54PGFK2G73GFIXA&field2='

# BH1750

BH1750_bus = smbus2.SMBus(0) 
BH1750_address = 0x77

# BMP280

BMP280_bus = SMBus(0) # Use bus 1 for I2C communication on most Orange Pi models
BMP280_address = 0x23  # BMP280 default I2C address

# Initialize BMP280 sensor
bmp_sensor = bmp280.BMP280(i2c_dev=BH1750_bus, i2c_addr=BH1750_address)

BH1750_bus.write_byte(BH1750_address, 0x10)
bytes_read = bytearray(2)

def get_value(BMP280_bus, BMP280address):
    write = i2c_msg.write(BMP280_address, [0x10])
    read = i2c_msg.read(BMP280_address, 2)
    BMP280_bus.i2c_rdwr(write, read)
    bytes_read = list(read)
    return (((bytes_read[0]&3)<<8) + bytes_read[1])/1.2

while True:
    temp = bmp_sensor.get_temperature()
    lux = get_value(BMP280_bus, BMP280_address)
    time.sleep(.5)
    print(f"temp = {temp}\nlux = {lux}")
    # requests.post(field2 +str(lux))
    # time.sleep(1)
    # requests.post(field1 +str(temp))
    # time.sleep(1)
    





