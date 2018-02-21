# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 17:04:48 2017

@author: diamond2nv @ github.com

esp001log json:
{
    "ESP_init": {
        "DATA_topic":"data-esp-test001"
        "DS3231 SetTime": "OK",
        "NTP & RTC SyncTime": "OK",
        "Time": "2017-12-09 05:26:09 GMT",
        "Day_W": 5,
        "Day_Y": 343,
        "DS3231 SQW": "1Hz Out Start0",
        "ambient Temperature": "18.548ºC",
        "ambient Humidity": "30.805%",
        "Sensor SHT30": "OK",
        "K Thermocouple": "15.500ºC",
        "Sensor MAX6675": "OK"
    }
}
"""

import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
from datetime import datetime
import pytz

i_hd = 0
data_time = ''
data_topic = ''
timestamp_esp = 0
GMT_FORMAT_ESP = '%Y-%m-%d %H:%M:%S GMT'

tz_cn = pytz.timezone('Asia/Shanghai')
NOW_TIME = datetime.now()
now_0 = NOW_TIME.timetuple()
timeStamp_now_0 = int(time.mktime(now_0))

def esp_Timestamp():
    global data_time
    if len(data_time) > 1:
        dt0 = datetime.strptime(data_time, GMT_FORMAT_ESP)
        tt0 = dt0.timetuple()
        timeStamp0 = int(time.mktime(tt0))
        dt = pytz.timezone('UTC').localize(dt0)
        dt = dt.astimezone(tz_cn)
        print("ESP Time:", dt.strftime('%Y-%m-%d %H:%M:%S'), ' @ ', dt.tzinfo)
        print("ESP Time:", dt.strftime('%Y-%m-%d %H:%M:%S'), ' @ ', dt.tzinfo, file=f_log)
        return timeStamp0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global data_topic
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esp001log")
    if len(data_time) > 1:
        client.subscribe(data_topic)
    #client.subscribe("esp001test")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global i_hd,data_time,data_topic
    global timestamp_esp
    #print(msg.topic+" "+str(msg.payload))
    if str(msg.topic)=="esp001log":
        i_lables_s = (msg.payload).decode()
        print(i_lables_s, file=f_log)
        try:
            i_lables = json.loads(i_lables_s)
            #print(json.dumps(i_lables_s, sort_keys=True, indent=4))
            data_time = i_lables['ESP_init']['Time']
            data_topic = i_lables['ESP_init']['DATA_topic']
            print('jTime:%s,\njDATA_topic=%s' % (data_time,data_topic), file=f_log)
            timestamp_esp = esp_Timestamp()
            print("esp_Timestamp =",timestamp_esp, file=f_log)
            print("esp_Timestamp =",timestamp_esp)
        except:
            timestamp_esp = int(time.time())
            data_topic = "esp001data"
            print("Error : json decode esp001log...")
            pass
        finally:
            if len(data_topic) > 1:
                client.subscribe(data_topic)
                print("client subscribe = %s" % data_topic)
    elif str(msg.topic)==data_topic:
        try:
            #i_data = json.loads((msg.payload).decode()[:-1])
            i_data = json.loads((msg.payload).decode())
            #print(j_data)
            #i_data = json.loads(j_data)
            #print(i_data[0]['id'],i_data[0]['kT'])
            #dfSeconds=np.array((i_data[0]['id'],i_data[0]['kT'],i_data[0]['aT'],i_data[0]['aH']),dtype=data_dt)
            df_id_index = int(timestamp_esp + i_data[0]['id'])
            dfSeconds=[[i_data[0]['kT'],i_data[0]['aT'],i_data[0]['aH']]]
            pdfSeconds = pd.DataFrame(dfSeconds,index=[df_id_index], columns=['kT', 'aT','aH'])
            #print(pdfSeconds)
            try:
                f_hdf.append(data_topic, pdfSeconds, format="table", append=True,data_columns=['kT', 'aT','aH'])
                i_hd = i_hd + 1
                if i_hd%600 == 0:
                    f_hdf.flush()
                    print(i_data[0]['id'],data_topic)
                else:
                    print(i_hd%600)
                #print(i_data[0]['id'],i_data[0]['kT'])
            except:
                print("f.append", file=f_log)
                raise
        except:
            print((msg.payload).decode(), file=f_log)
            pass
    else:
        pass


def main():
    print("Runing...", NOW_TIME.strftime("%Y-%m-%d %H:%M:%S"),file=f_log)
                         #将数据写入文件的主键data下面
    client = mqtt.Client('HASEE3543189')
    client.on_connect = on_connect
    client.on_message = on_message
    global f_hdf
    with pd.HDFStore("Seconds.hdf5","a", complevel=9, complib='zlib') as f_hdf:
        client.connect("222.195.68.253", port=1883,keepalive=0)
        client.loop_forever()


if __name__ == '__main__':
    with open("esp001log.log","w",encoding='utf-8') as f_log:
        main()
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
