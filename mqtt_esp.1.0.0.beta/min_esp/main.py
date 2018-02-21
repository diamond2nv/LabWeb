import my_app
from machine import Pin,reset
from utime import sleep_ms
sleep_ms(1000)
pin = Pin(13, Pin.IN, Pin.PULL_UP)
while True:
    if pin.value():
        try:
            my_app.kmain()
        except:
            reset()
    else:
        sleep_ms(200)