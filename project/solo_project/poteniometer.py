import threading
import wiringpi
import time

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
            lux_threshold = read_lux_threshold(0)
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
            count += 1  # Example action
            time.sleep(0.1)

# Setup and main code here

if __name__ == "__main__":
    pin_CS_adc = 16  # We will use w16 as CE, not the default pin w15!
    button_pin = 3
    pwn_led = 4
    red_led = 5
    orange_led = 7
    green_led = 8
    count = 0
    lux_threshold = 500
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
    wiringpi.pinMode(pwn_led, 1)       # Set pin 6 to 1 ( OUTPUT )
    wiringpi.digitalWrite(pwn_led ,1)
    

    # Create and start sensor reading thread
    sensor_thread = threading.Thread(target=sensor_reading_task)
    sensor_thread.daemon = True  # Daemonize the thread to terminate with main thread
    sensor_thread.start()

    # Create and start button polling thread
    button_thread = threading.Thread(target=button_polling_task)
    button_thread.daemon = True  # Daemonize the thread to terminate with main thread
    button_thread.start()

    # Main code continues here
    try:
        while True:
            alerting_led_for_temp()
            print(f"lux = {lux} // Threshold = {lux_threshold}\ntemp = {temperature} // Threshold = {temp_threshold}\n")
            time.sleep(0.1)

    except KeyboardInterrupt:
        DeactivateADC()
        wiringpi.digitalWrite(green_led, 0)
        wiringpi.digitalWrite(orange_led, 0)
        wiringpi.digitalWrite(red_led, 0)
        wiringpi.digitalWrite(pwn_led , 0)
        print("\nProgram terminated")


