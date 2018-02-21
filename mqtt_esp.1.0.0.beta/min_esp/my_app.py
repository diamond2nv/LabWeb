from utime import sleep_ms
from umqtt_simple import MQTTClient
from machine import Pin,unique_id
from micropython import schedule,alloc_emergency_exception_buf
from esp_init import ESP_init
import uheapq
from max6675 import MAX6675
from sht30 import SHT30
from ds3231_time import cl_id
import gc
alloc_emergency_exception_buf(100)
sensor_k = MAX6675()
sensor3 = SHT30()
button = Pin(0, Pin.IN)
SERVER = "192.168.100.101"
CLIENT_ID = cl_id()
TOPIC = b"esp001log"
DATA_TP = b"data_"+CLIENT_ID
sub_flag = 100
i_pum = 0
i_snd = 0
i_data=[]
uheapq.heapify(i_data)
class Foo():
    def __init__(self):
        self.push_ref = self.push
        p2 = Pin(2, Pin.IN)
        p2.irq(trigger=Pin.IRQ_RISING, handler=self.cb)
    def push(self, _):
        global i_pum,i_snd,i_data,sub_flag
        if -35 < (i_pum-i_snd) < 61:
            try:
                kT = sensor_k.measure()
                kTr = '%f' % (kT)
                if kTr == 'nan':
                    kTr = 'null'
            except:
                kTr = 'null'
                pass
            try:
                aT, aH = sensor3.measure()
                aTr = '%f' % (aT)
                aHr = '%f' % (aH)
                if aTr == 'nan':
                    aTr = 'null'
                if aHr == 'nan':
                    aHr = 'null'
            except:
                aTr = 'null'
                aHr = 'null'
                pass
            atemp ='[{"id":%d,"kT":%s,"aT":%s,"aH":%s}]' % (i_pum,kTr,aTr,aHr)
            uheapq.heappush(i_data,atemp)
        else:
            pass
        i_pum += 1
        if i_pum>43200:
            sub_flag = 404
    def cb(self, t):
        schedule(self.push_ref, 0)
def kmain(server=SERVER):
    global sub_flag,i_pum,i_snd,i_data
    f_snd = 0
    c = MQTTClient(CLIENT_ID, server)
    try:
        hello_i = ESP_init(DATA_TP)
        c.connect()
        c.publish(TOPIC, hello_i, retain=True, qos=1)
        sleep_ms(10)
        c.disconnect()
        sleep_ms(50)
        c.connect()
        c.set_last_will(DATA_TP, b"<Connect_lost>", retain=True, qos=1)
        sleep_ms(10)
        c.publish(DATA_TP, b"<Data_begin>", retain=True, qos=1)
        sleep_ms(10)
        gc.collect()
        while sub_flag != 404:
            foobar = Foo()
            f_snd = 0
            while button.value() != 0 and sub_flag == 100:
                try:
                    if f_snd == 0 or i_pum - i_snd > 60:
                        str_data = uheapq.heappop(i_data)
                    try:
                        c.publish(DATA_TP, str_data, retain=True, qos=1)
                        sleep_ms(10)
                        f_snd = 0
                        i_snd += 1
                    except:
                        f_snd += 1
                        gc.collect()
                        if f_snd > 30:
                            sub_flag = 104
                        else:
                            try:
                                c.connect()
                                sleep_ms(200)
                            except:
                                try:
                                    import boot
                                except:
                                    pass
                                sleep_ms(200)
                                pass
                        pass
                except:
                    i_snd = i_pum
                    sleep_ms(10)
                    pass
            if sub_flag == 104:
                sub_flag = 404
                raise
            sleep_ms(50)
            if button.value() == 0 and sub_flag == 101:
                sleep_ms(2000)
                if button.value() == 0:
                    sub_flag = 100
                    sleep_ms(2000)
            if button.value() == 0 and sub_flag == 100:
                sleep_ms(2000)
                if button.value() == 0:
                    sub_flag = 101
                    sleep_ms(2000)
    except:
        pass
    finally:
        try:
            del foobar
        except:
            pass
        c.publish(DATA_TP, b"<Data_end>", retain=True, qos=1)
        sleep_ms(50)
        c.disconnect()
        raise
if __name__ == "__main__":
    kmain()