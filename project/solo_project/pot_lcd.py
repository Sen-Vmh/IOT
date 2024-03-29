import wiringpi
import time
from ClassLCD import LCD, ActivateLCD, DeactivateLCD

def read_temperature_threshold(adc_number):
    if ((adc_number > 7) or (adc_number < 0)):
        return -1
    revlen, recvData = wiringpi.wiringPiSPIDataRW(1, bytes([1,(8+adc_number)<<4,0]))
    time.sleep(0.000005)
    adc_output = ((recvData[1]&3) << 8) + recvData[2]
    return(adc_output)

print(read_temperature_threshold(0))