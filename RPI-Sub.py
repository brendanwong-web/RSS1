#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.


import paho.mqtt.client as mqtt
import csv
import time
import datetime


def topic_init(topic, header):
    f = open(f'./{topic}.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()
    print('written header in ' + topic)

def on_connect(mqttc, obj, flags, reason_code):
    print("reason_code: " + str(reason_code))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    '''if msg.topic == 'weight':
        print('Message received on ' + msg.topic)
        time = datetime.datetime.now()
        timef = time.strftime('%d/%m/%Y %H:%M')
        with open(f'./{msg.topic}.csv', 'a') as f:
            try:
                data = [timef, float(msg.payload)]
            except:
                print('msg is not float convertible')
                data = [timef, msg.payload]
            writer = csv.writer(f)
            writer.writerow(data)
            print('data written')
    elif msg.topic == 'usnd':
        print('Message received on ' + msg.topic)
        time = datetime.datetime.now()
        timef = time.strftime('%d/%m/%Y %H:%M')
        with open(f'./{msg.topic}.csv', 'a') as f:
            try:
                data = [timef, float(msg.payload)]
            except:
                print('msg is not float convertible')
                data = [timef, msg.payload]
            writer = csv.writer(f)
            writer.writerow(data)
            print('data written')'''


def on_subscribe(mqttc, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))


def on_log(mqttc, obj, level, string):
    print(string)


# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("172.20.10.10", 1883, 60)
mqttc.subscribe("plastic")
mqttc.subscribe("gtpc")
mqttc.subscribe("unlck")
mqttc.subscribe("logger")

mqttc.loop_forever()
