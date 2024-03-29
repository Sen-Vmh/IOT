import time
import smbus2
import bmp280

# Initialize I2C bus
bus = smbus2.SMBus(0)  # Use bus 1 for I2C communication on most Orange Pi models
address = 0x77  # BMP280 default I2C address

# Initialize BMP280 sensor
bmp_sensor = bmp280.BMP280(i2c_dev=bus, i2c_addr=address)

while True:
    temp = bmp_sensor.get_temperature()
    # pressure = bmp_sensor.get_pressure()
    print(f"temperature {temp}")
    time.sleep(1)
