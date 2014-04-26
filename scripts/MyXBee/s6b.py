"""
zigbee.py

By Deng Shuan, 2014
Inspired by code written by Paul Malmsten, 2010
Inspired by code written by Amit Synderman and Marco Sangalli
gdrapp@gmail.com

This module implements an XBee WIFI (ZigBee) API library.
"""
import struct
from .base import XBeeBase
from .python2to3 import byteToInt, intToByte

class S6B(XBeeBase):
    """
    Provides an implementation of the XBee API for XBee WIFI (ZigBee) modules
    with recent firmware.
    
    Commands may be sent to a device by instantiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device synchronously by calling wait_read_frame.
    For asynchronous reads, see the defintion of XBeeBase.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':b'\x08'},
                         {'name':'frame_id',  'len':1,      'default':b'\x01'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':b'\x09'},
                         {'name':'frame_id',  'len':1,      'default':b'\x01'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':b'\x07'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         {'name':'dest_addr',  'len':8,        'default':struct.pack('>Q', 0)},
                         {'name':'options',         'len':1,        'default':b'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "zigbee_remote_at": # recommand remote_at(0x04) to send remote command
                        [{'name':'id',              'len':1,        'default':b'\x17'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':struct.pack('>Q', 0)},
                         {'name':'reserved',        'len':2,        'default':b'\xFF\xFE'},
                         {'name':'options',         'len':1,        'default':b'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "zigbee_tx": # recommand tx_ipv4(0x20) for data transmission
                        [{'name':'id',              'len':1,        'default':b'\x10'},
                         {'name':'frame_id',        'len':1,        'default':b'\x01'},
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'reserved',        'len':3,        'default':b'\xFF\xFE\x00'},
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "zigbee_tx_explicit": # recommand tx_ipv4(0x20) for data transmission
                        [{'name':'id',              'len':1,        'default':b'\x11'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'reserved',        'len':3,        'default':b'\xFF\xFE\xE6'},
                         {'name':'dest_endpoint',   'len':1,        'default':None},
                         {'name':'cluster',         'len':2,        'default':None},
                         {'name':'reserved',        'len':3,        'default':b'\xC1\x05\x00'},
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "tx_64":
                        [{'name':'id',              'len':1,        'default':b'\x00'},
                         {'name':'frame_id',        'len':1,        'default':b'\x01'},
                         {'name':'dest_addr',       'len':8,        'default':struct.pack('>Q', 0)},
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "tx_ipv4":
                        [{'name':'id',              'len':1,        'default':b'\x20'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         {'name':'dest_addr_ipv4',  'len':4,        'default':None},
                         {'name':'dest_port',       'len':2,        'default':b'\x26\x16'},
                         {'name':'src_port',        'len':2,        'default':b'\x26\x16'},
                         {'name':'protocol',        'len':1,        'default':b'\x00'},
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'rf_data',         'len':None,     'default':None}]
                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parse_as_io_samples:name of field to parse as io
    #           }
    #           ...
    #        }
    #
    api_responses = {b"\x90":
                        {'name':'rx',
                         'structure':
                            [{'name':'src_addr',        'len':8},
                             {'name':'reserved',        'len':2},
                             {'name':'options',         'len':1},
                             {'name':'rf_data',         'len':None}]},
                     b"\x80":
                        {'name':'rx_64',
                         'structure':
                            [{'name':'src_addr',        'len':8},
                             {'name':'rssi',            'len':1},
                             {'name':'options',         'len':1},
                             {'name':'rf_data',         'len':None}]},
                     b"\x91":
                        {'name':'zigbee_rx_explicit',
                         'structure':
                            [{'name':'src_addr',        'len':8},
                             {'name':'reserved',        'len':2},
                             {'name':'src_endpoint',    'len':1},
                             {'name':'dest_endpoint',   'len':1},
                             {'name':'cluster',         'len':2},
                             {'name':'profile',         'len':2},
                             {'name':'options',         'len':1},
                             {'name':'rf_data',         'len':None}]},
                     b"\x8b":   # recommand tx_status(0x89) to send transmission response
                        {'name':'zigbee_tx_status',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'reserved',        'len':3},
                             {'name':'status',          'len':1},
                             {'name':'reserved',        'len':1}]},
                     b"\x89":
                        {'name':'tx_status',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'status',          'len':1}]},
                     b"\x8a":
                        {'name':'status',
                         'structure':
                            [{'name':'status',      'len':1}]},
                     b"\x87": #Checked GDR (not sure about parameter, could be 4 bytes)
                        {'name':'remote_command_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'src_addr',        'len':8},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}],
                          'parsing': [('parameter',
                                       lambda self, original: self._parse_IS_at_response(original))]
                             },
                     b"\x88":
                        {'name':'at_response',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'command',     'len':2},
                             {'name':'status',      'len':1},
                             {'name':'parameter',   'len':None}],
                         'parsing': [('parameter',
                                       lambda self, original: self._parse_IS_at_response(original))]
                             },
                     b"\x97": # recommand remote_command_response(0x87) to generate response
                        {'name':'zigbee_remote_command_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'src_addr',        'len':8},
                             {'name':'reserved',        'len':2},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}],
                          'parsing': [('parameter',
                                       lambda self, original: self._parse_IS_at_response(original))]
                             },
                     b"\xb0":
                        {'name':'rx_ipv4',
                         'structure':
                            [{'name':'frame_id',          'len':1},
                             {'name':'src_addr_ipv4',     'len':4},
                             {'name':'dest_port',         'len':2},
                             {'name':'src_port',          'len':2},
                             {'name':'protocol',          'len':1},
                             {'name':'status',            'len':1},
                             {'name':'rf_data',           'len':None}]
                             },
                     }
    
    def _parse_IS_at_response(self, packet_info):
        """
        If the given packet is a successful remote AT response for an IS
        command, parse the parameter field as IO data.
        """
        if packet_info['id'] in ('at_response','remote_command_response') and packet_info['command'].lower() == b'is' and packet_info['status'] == b'\x00':
               return self._parse_samples(packet_info['parameter'])
        else:
            return packet_info['parameter']
            

    
    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(S6B, self).__init__(*args, **kwargs)

    def _parse_samples_header(self, io_bytes):
        """
        _parse_samples_header: binary data in XBee WIFI IO data format ->
                        (int, [int ...], [int ...], int, int)
                        
        _parse_samples_header will read the first three bytes of the 
        binary data given and will return the number of samples which
        follow, a list of enabled digital inputs, a list of enabled
        analog inputs, the dio_mask, and the size of the header in bytes

        _parse_samples_header is overloaded here to support the additional
        IO lines offered by the XBee WIFI
        """
        header_size = 4

        # number of samples (always 1?) is the first byte
        sample_count = byteToInt(io_bytes[0])
        
        # bytes 1 and 2 are the DIO mask; bits 9 and 8 aren't used
        dio_mask = (byteToInt(io_bytes[1]) << 8 | byteToInt(io_bytes[2])) & 0x0E7F
        
        # byte 3 is the AIO mask
        aio_mask = byteToInt(io_bytes[3])
        
        # sorted lists of enabled channels; value is position of bit in mask
        dio_chans = []
        aio_chans = []
        
        for i in range(0,13):
            if dio_mask & (1 << i):
                dio_chans.append(i)
        
        dio_chans.sort()
        
        for i in range(0,8):
            if aio_mask & (1 << i):
                aio_chans.append(i)
        
        aio_chans.sort()
        
        return (sample_count, dio_chans, aio_chans, dio_mask, header_size)
