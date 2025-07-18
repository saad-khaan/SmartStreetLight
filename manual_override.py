'''
Manual Override button for Smart lighting system
Written by: Saad
'''


import machine
import utime
led_external = machine.Pin(15, machine.Pin.OUT)
button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
#Defining "led_external" and "button", which are defined to be located pins on the pico board.

while True:
    if button.value() == 1:
        led_external.value(1)
    utime.sleep(2)
        led_external.value(0)

#infinite loop if the button is pressed, the led will turn on. When button is released, it will wait 2 seconds and turn off.
#Acting as a manual override incase of system malfunctioning.