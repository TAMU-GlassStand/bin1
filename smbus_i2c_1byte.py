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
	read=bus.read_i2c_block_data(address, 0, 6)
	read1=read[0]
	read2=read[1]
	read3=read[2]
	read4=read[3]
	read5=read[4]
	read6=read[5]

 
	print "Byte Output is: %s" % bus.read_i2c_block_data(address, 0, 6)
	time.sleep(1)
	read=bus.read_i2c_block_data(address, 0, 6)
	print "Read Output is: %s" % read
	time.sleep(1)
	print "Bit1 is: %s" % read1
	print "Bit2 is: %s" % read2
	print "Bit3 is: %s" % read3
	print "Bit4 is: %s" % read4
	print "Bit5 is: %s" % read5
	print "Bit6 is: %s" % read6
