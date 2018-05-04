#!/usr/bin/python

from smbus2 import SMBus
import time

busnum = 1

#OPT3001 sensors can have I2C addresses of x44, x45, x46, x47
#0x44 is the default address for the light sensor EVM

address1 = 0x44
address2 = 0x45

go = true
while go
	bus = SMBus(busnum)
	b1 = bus.write_word_data(address1, 0x01, 0x10c4)
	b2 = bus.write_word_data(address2, 0x01, 0x10c4)
	print b1
	print b2

	#setup an I2C message to read data from address for testing
	numBytes = 2
	
	# b = bus.read_byte_data(address,0)
	#b = bus.read_word_data(address, 0)
	#0 in lines above is "offset"
	print "data test1: %s" % bus.read_word_data(address1, 0)
	print "data test2: %s" % bus.read_word_data(address2, 0)
	
	bus.close() #close the i2c bus communication line

