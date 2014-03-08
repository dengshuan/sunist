#-*- coding:utf-8 -*-
#!/usr/bin/env python
"""
Initialize xbee modules and redis.

configuration file: config.json
"""

# from __future__ import unicode_literals
import json
import serial
import time
from redis import Redis
from xbee import ZigBee

# available xbee
# 8D9B59,8D9BDC; 8D956F,8D9BDE,8D9419,98B472
ser = serial.Serial('/dev/ttyUSB0', 9600)
xbee = ZigBee(ser)

config_file = 'config.json'

redis = Redis()

json_data = open(config_file)
print 'Loading configuration file {} ...'.format(config_file)
data = json.load(json_data)
modules = data['module']
# remove previous settings
keys = redis.keys('xbee:*')
print "Warning: I'll delete all xbee data in redis..."
for k in keys:
    redis.delete(k)
# set redis using configuration file



port = ['D{}'.format(i) for i in range(8)]

for idx, mod in enumerate(modules):
    # setting redis
    module = {}
    module['id'] = idx
    module['name'] = mod['name']
    module['address'] = mod['address']
    module['io'] = []
    module['D'] = [mod['D{}'.format(i)] for i in range(8)]
    for i in range(8):
        if mod['D{}'.format(i)] == 2:
            module['io'].append(0) # adc
        elif mod['D{}'.format(i)] in range(3,6):
            module['io'].append(False) # dio
        else:
            module['io'].append(None) # not used
    redis.hmset('xbee:{}'.format(idx), module)
    redis.hset('xbee:lookup:address', module['address'], idx)
    redis.hset('xbee:lookup:name', module['name'], idx)
    address = mod['address']
    # setting xbees
    addr = ''
    counts = 0
    for i in range(8):
        addr += chr(int('0x'+address[2*i:2*(i+1)],16))
    for p in port:
        xbee.remote_at(frame_id='I', dest_addr_long=addr, command=p, parameter=chr(mod[p]))
        time.sleep(0.001)
        response = xbee.wait_read_frame()
        if response['status'] != '\x00':
            counts += 1
            print u'Warning: {} {} setting failed!'.format(module['name'],p)

if counts == 0:
    print 'All ZigBee modules initialized successfully!'
else:
    print '{} port(s) setting failed! Please check your configuration file'.format(counts)
