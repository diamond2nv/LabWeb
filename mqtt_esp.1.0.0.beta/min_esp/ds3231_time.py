from urtc import DS3231
from machine import I2C, Pin, RTC, unique_id
from ubinascii import hexlify
i2c = I2C(scl=Pin(5), sda=Pin(4))
rtc = DS3231(i2c)
def lost_time():
    return rtc.lost_power()
def settime():
    tm = rtc.datetime()
    RTC().datetime([i for i in tm[:-1]]+[0])
def sync_rtc2ntp():
    import ntptime_cn
    rtc.datetime(ntptime_cn.get_ntp2rtc())
    print("sync_rtc2ntp")
def sqw_1hz():
    return rtc.sqw_1hz()
def cl_id():
    return b"esp_" + hexlify(unique_id())