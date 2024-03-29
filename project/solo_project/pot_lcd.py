import wiringpi
import time
from ClassLCD import LCD, ActivateLCD, DeactivateLCD

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
    return adc_output

def read_lux_threshold(adc_number):
    if ((adc_number > 7) or (adc_number < 0)):
        return -1
    revlen, recvData = wiringpi.wiringPiSPIDataRW(1, bytes([1,(8+adc_number)<<4,0]))
    time.sleep(0.000005)
    adc_output = ((recvData[1]&3) << 8) + recvData[2]
    return adc_output

# Setup
pin_CS_adc = 16 # CE pin for ADC
wiringpi.wiringPiSetup()
wiringpi.pinMode(pin_CS_adc, 1) # Set CE pin to OUTPUT
wiringpi.wiringPiSPISetupMode(1, 0, 500000, 0) #(channel, port, speed, mode)

# LCD Pins
PINS = {
    'CS' : 13, # CE
    'RST' : 10,
    'DC' : 9, 
    'DIN' : 16,
    'SCLK' : 14, 
    'LED' : 6,
}

# Initialize LCD
wiringpi.wiringPiSetup()
wiringpi.wiringPiSPISetupMode(1, 0, 400000, 0) # (channel, port, speed, mode)
wiringpi.pinMode(PINS['CS'] , 1) # set CE pin to mode 1 (output)
ActivateLCD(PINS['CS'])
lcd_1 = LCD(PINS)

# Main
try:
    lcd_1.clear()
    lcd_1.set_backlight(2)
    while True:
        ActivateADC()
        
        temp = read_temperature_threshold(1)
        print(temp)
        lux = read_lux_threshold(0)
        DeactivateADC()

        # Display values on LCD
        ActivateLCD(PINS['CS'])
        lcd_1.clear() # Clear buffer
        lcd_1.go_to_xy(0, 0) # Set starting position
        lcd_1.put_string(f'Temp: {temp} Lux: {lux}') # Print values to buffer
        lcd_1.refresh() # Update the LCD with the buffer
        DeactivateLCD(PINS['CS'])

        time.sleep(1)

except KeyboardInterrupt:
    # Deactivate the LCD after program termination
    lcd_1.clear()
    lcd_1.refresh()
    lcd_1.set_backlight(0)
    DeactivateLCD(PINS['CS'])
    print("\nProgram terminated")
