import utime
import ntptime_cn
import ds3231_time as ds_tm
from max6675 import MAX6675
from sht30 import SHT30
from uio import StringIO
def ESP_init(cl_s=b'esp001data'):
    f_log = StringIO()
    f_log.write('{"ESP_init":{\n')
    atemp = '"DATA_topic":"%s",\n' %(cl_s.decode())
    print(atemp)
    f_log.write(atemp)
    try:
        if ds_tm.lost_time():
            atemp = '"DS3231":"lost_time",\n'
            print(atemp)
            f_log.write(atemp)
            raise
        else:
            ds_tm.settime()
            atemp = '"DS3231 SetTime":"OK",\n'
            print(atemp)
            f_log.write(atemp)
            try:
                ntptime_cn.time()
                utime.sleep_ms(200)
                ntptime_cn.settime()
                ds_tm.sync_rtc2ntp()
                ds_tm.settime()
                atemp = '"NTP & RTC SyncTime":"OK",\n'
                print(atemp)
                f_log.write(atemp)
            except:
                pass
    except:
        ntptime_cn.time()
        utime.sleep(3)
        ntptime_cn.settime()
        atemp = '"NTP SetTime":"OK",\n'
        print(atemp)
        f_log.write(atemp)
        try:
            ds_tm.sync_rtc2ntp()
            ds_tm.settime()
            atemp = '"NTP & RTC SyncTime":"OK",\n'
            print(atemp)
            f_log.write(atemp)
        except:
            pass
    finally:
        atemp = '"Time":"%d-%02d-%02d %02d:%02d:%02d GMT",\n"Day_W":%d,"Day_Y":%d,\n' % (utime.localtime())
        print(atemp)
        f_log.write(atemp)
    try:
        atemp = '"DS3231 SQW":"1Hz Out Start%d",\n' % (ds_tm.sqw_1hz())
        print(atemp)
        f_log.write(atemp)
    except:
        atemp = '"DS3231 SQW":"1Hz Out ERROR",\n'
        print(atemp)
        f_log.write(atemp)
    try:
        sensor3 = SHT30()
        temperature, humidity = sensor3.measure()
        del sensor3
        atemp ='"ambient Temperature":"%f ºC","ambient Humidity":"%f %%",\n' % (temperature, humidity)
        print(atemp)
        f_log.write(atemp)
        atemp ='"Sensor SHT30":"OK",\n'
        print(atemp)
        f_log.write(atemp)
    except:
        pass
    try:
        sensor_k = MAX6675()
        atemp ='"K Thermocouple":"%f ºC",\n"Sensor MAX6675":"OK"}}..' % (sensor_k.measure())
        del sensor_k
        print(atemp)
        f_log.write(atemp)
    except:
        pass
    f_str = f_log.getvalue()
    f_log.close()
    return f_str
if __name__ == '__main__':
    ESP_init()
