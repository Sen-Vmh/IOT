import time
from smbus2 import SMBus, i2c_msg

bus = SMBus(0)
address = 0x23 

bus.write_byte(address, 0x10)
bytes_read = bytearray(2)

def get_value(bus, address):
    write = i2c_msg.write(address, [0x10])
    read = i2c_msg.read(address, 2)
    bus.i2c_rdwr(write, read)
    bytes_read = list(read)
    return (((bytes_read[0]&3)<<8) + bytes_read[1])/1.2

while True:
    lux = get_value(bus, address)
    print("{:.2f} lux".format(lux))
    time.sleep(1)

