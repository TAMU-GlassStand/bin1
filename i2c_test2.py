#!/usr/bin/python

from smbus2 import SMBus
from smbus2 import SMBusWrapper
import time


address1 = 0x44
address2 = 0x45
busnum = 1

config = 0x10c4 #for exponent mask = unmasked
#config = 0x14c4 #for exponent mask = masked

bus = SMBus(busnum)
try:
	b1 = bus.write_word_data(address1, 0x01, config)
	print b1
except IOError:
	print("sensor 1 not connected")
try:
	b2 = bus.write_word_data(address2, 0x01, config)
	print b2
except IOError:
	print("sensor 2 not connected")
bus.close()

#bus = SMBus(busnum)
with SMBusWrapper(busnum) as bus1:
	while 1:
		try:
			w1 = bus1.read_word_data(address1, 0)
			# print "data test1: ", w1, " ", hex(w1)
			w1 = format(w1, '016b')
			bin1 = w1[8:16] + w1[0:8]
			# print "data test1: ", bin1
			exp1 = int( bin1[0:4], 2 )
			lux1 = 0.01*(2**exp1)*int( bin1[4:16], 2)
			print "data test1: ", lux1
		except IOError:
			print "IOError-sensor disconnected"
		
		try:
			w2 = bus1.read_word_data(address2, 0)
			# print "data test2: ", w1, " ", hex(w2)
			w2 = format(w2, '016b')
			bin2 = w2[8:16] + w2[0:8]
			# print "data test2: ", bin2
			exp2 = int( bin2[0:4], 2 )
			lux2 = 0.01*(2**exp2)*int( bin2[4:16], 2)
			print "data test2: ", lux2
		except IOError:
			print "IOError-sensor disconnected"
		
		print "\n"
		time.sleep(0.1)
