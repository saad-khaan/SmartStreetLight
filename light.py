import machine
import utime

LDR=machine.ADC(26)

led=machine.Pin(15, machine.Pin.OUT)

while True:
    if (LDR.read_u16())>= 30000:
        led.value(1)
    else:
        led.value(0)
