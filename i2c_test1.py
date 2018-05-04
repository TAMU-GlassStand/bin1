#!/usr/bin/python

from smbus2 import SMBus
from smbus2 import SMBusWrapper
import time

address1 = 0x44
address2 = 0x45
busnum = 1

bus = SMBus(busnum)
#b1 = bus.write_word_data(address1, 0x01, 0x10c4)
#print b1
#bus.close()

file = open('/home/pi/bin/i2cout.txt','w')

bus = SMBus(busnum)
with SMBusWrapper(busnum) as bus1:
	while 1:
		w1 = bus1.read_word_data(address1, 0)
		# print "data test1: ", w1, " ", hex(w1)
		w1 = format(w1, '016b')
		bin1 = w1[8:16] + w1[0:8]
		# print "data test1: ", bin1
		exp1 = int( bin1[0:4], 2 )
		lux1 = 0.01*(2**exp1)*int( bin1[4:16], 2)
		print "data test1: ", lux1
		
		file.write( str(lux1) + '\n' )
		time.sleep(1)
