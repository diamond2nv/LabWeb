import gc
gc.collect()
from utime import sleep
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('**', '***')#your wifi ssid & code
        f_b = 0
        while not wlan.isconnected() and f_b < 30:
            sleep(1)
            f_b = f_b + 1
            pass
    try:
        print('network config:', wlan.ifconfig())
    except:
        print('WiFi is', wlan.isconnected())
        pass

do_connect()