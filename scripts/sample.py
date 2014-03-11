#!/usr/bin/env python
import serial
from xbee import ZigBee
from redis import Redis
import time
import json
import ast
import threading
import signal
import os
import struct

redis = Redis()
ser = serial.Serial('/dev/ttyUSB0',9600, timeout=1)
xbee = ZigBee(ser)

address = redis.hgetall('xbee:lookup:address')

def transAddr(addr):
    if len(addr) == 16:                         # string -> hex
        l = [addr[2*i:2*i+2] for i in range(8)] # split addr
        il = [int(i,16) for i in l]             # change to int list
        return struct.pack('>8B', *il)
    elif len(addr) == 8:        # hex -> string
        l = map(ord, addr)
        f = '{:02x}' * 8
        return f.format(*l)

# monitor: Dn=2(ADC)  Dn=3(DI)
# control: Dn=4(DO low)   Dn=5(DO high)

def listen():
    x = redis.pubsub()
    x.subscribe('xbee:cmd')
    for msg in x.listen():
        if msg['type'] == 'message':
            global G_ADDR, G_CMD, G_PARA
            G_ADDR, G_CMD, G_PARA = ast.literal_eval(msg['data'])
            os.kill(pid, signal.SIGUSR1)


def control(signum, stack):
    """Pause sampling to set module."""
    print 'Waiting for module to be set...'
    # print map(type,[transAddr(G_ADDR), G_CMD, G_PARA])
    xbee.remote_at(frame_id='C', dest_addr_long=transAddr(G_ADDR), command=str(G_CMD), parameter=chr(G_PARA))
    time.sleep(0.1)
    print 'Setting remote module done, you can continue sampling now'

signal.signal(signal.SIGUSR1, control)

if __name__ == '__main__':
    pid = os.getpid()
    listen_thread = threading.Thread(target=listen)
    listen_thread.setDaemon(True)
    listen_thread.start()
    while True:
        try:
            print 'Sampling...'
            for d, idx in address.items():
                # addr = ''
                # for i in range(8):
                #     addr += chr(int('0x'+d[2*i:2*(i+1)],16))
                addr = transAddr(d)
                xbee.remote_at(frame_id='S', dest_addr_long=addr, command='IS')
                time.sleep(0.1)
                response = xbee.wait_read_frame()
                if response['status'] == '\x00' and response['frame_id'] == 'S':
                    sample = response['parameter'][0]
                    response_addr = response['source_addr_long']
                    print transAddr(response_addr), sample
                    data = []
                    for i in range(8):
                        if 'dio-{}'.format(i) in sample.keys():
                            data.append(sample['dio-{}'.format(i)])
                        elif 'adc-{}'.format(i) in sample.keys():
                            data.append(sample['adc-{}'.format(i)])
                        else:
                            data.append(None)
                    myid = redis.hget('xbee:lookup:address', transAddr(response_addr))
                    redis.hset('xbee:{}'.format(myid), 'io', data)
        except KeyboardInterrupt:
            xbee.halt()
            ser.close()
            break
