'''
Temperature reader
Written by: Saad
'''

import machine
import utime
sensor_temp = machine.ADC(4)
#Defining 'sensor_temp' to locate the temperature sensor on breadboard.

while True:
    reading = sensor_temp.read_u16()
    temperature = 27 - (reading - 0.706)/0.001721 #Converts voltage reading to Celcius
    print(temperature) 
    utime.sleep(2)

'''
Infinite loop which converts the temperature reading to celcius, and then prints the recorded temperature. 
This code will act as our maintenance portion of the system, to log in situations of overheating by reading the temperature.

Our UI has a green, yellow, and red light on the top right. This code will eventually be programmed to work with that depending on the temperature of the system.
This will allow us to record and log the maintenance of the street lights.
'''


