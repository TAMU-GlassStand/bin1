#!/usr/bin/python

from smbus2 import SMBus
import time

short_status = 0xd0
long_status = 0xd1

delay = 0.1

bus = SMBus(1)
passed = 0
while passed==0:
	try:
		time.sleep(delay)
		bus.write_byte_data(0x1b, 0x36, short_status)
		#bus.write_byte_data(0x1b, 0x36, long_status)
		time.sleep(delay)
		print("read request executed")
		bus.write_byte_data(0x1b, short_status, 0x00)
		#bus.write_byte_data(0x1b, long_status, 0x00)
		print("write zeros executed")
		time.sleep(delay)
		data = bus.read_byte_data(0x1b, 0x37)	#read for short status
		#data = bus.read_i2c_block_data(0x1b, 0x37, 4)	#read for long status
		print( hex(data) )
		passed = 1
	except IOError:
		print("failed execution; restarting loop")
bus.close()