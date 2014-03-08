#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
import serial
import time
from xbee import ZigBee

if len(sys.argv) == 2:
  PORT = sys.argv[1]
  print "I'm listening {}".format(PORT)
else:
  PORT = '/dev/ttyUSB0'
  print "I'm listening default port: {}".format(PORT)
BAUD_RATE = 9600


ser = serial.Serial(PORT, BAUD_RATE)


def print_data(data):
  print data

xbee = ZigBee(ser)

success = '\x00'
cmd = 'SL'

# xbee.send('at',frame_id='A',command=cmd)
# time.sleep(0.001)
# response = xbee.wait_read_frame()
# if response['status'] == success and response['frame_id'] == 'A'\
#    and response['command'] == cmd:
#     print response['parameter']

while True:
  try:
    response = xbee.wait_read_frame()
    print response
    # if response['status'] == '\x00' and response['frame_id'] == 'S':
    #   sample = response['parameter'][0]
    #   data = []
    #   for i in range(8):
    #     if 'dio-{}'.format(i) in sample.keys():
    #       data.append(sample['dio-{}'.format(i)])
    #     elif 'adc-{}'.format(i) in sample.keys():
    #       data.append(sample['adc-{}'.format(i)])
    #     else:
    #       data.append(None)
    #   print data
  except KeyboardInterrupt:
    break
    xbee.halt()
    ser.close()
