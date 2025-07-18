'''
IR Receiver to detect human presence and activity.
Written by: Saad Khan
'''

import utime

led = machine.Pin(14, machine.Pin.OUT)
IR_emitter = machine.Pin(15, machine.Pin.OUT)
IR_receiver = machine.ADC(26)
#Defining "led", "IR_emitter", and "IR_receiver" to be locations on the breadboard and PICO board.

while True:
    print(IR_receiver.read_u16())
    
    utime.sleep(0.2)

    IR_emitter.value(1) 

    if(IR_receiver.read_u16()>60000):
        led.value(1)
    else:
        led.value(0)

'''
Infinite loop which turns on the IR emitting LED, and checks if the IR receiving output is within the set threshold (60000). 
If it is, then the led will turn on, indicating human presence, otherwise it will turn off.
'''


