#!/usr/bin/python

from smbus2 import SMBus
from smbus2 import SMBusWrapper
import time

busnum=1
address=0x0a
offset=0x00
data0=[0, 0, 0, 0, 0, 0]
bus=SMBus(busnum)
b=bus.read_byte_data(address,offset)
print b


while 1:
	
	bus.write_i2c_block_data(0x0a, 0x00, data0) 
	print "Byte Output is: %s" % bus.read_i2c_block_data(address, 0, 6)
	time.sleep(0.1)
