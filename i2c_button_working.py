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


prev = -1
touch = -1
touchbit = -1
while 1:
	
	bus.write_i2c_block_data(0x0a, 0x00, data0) #Write which sensor element looking for (buttons)
	read=bus.read_i2c_block_data(address, 0, 6)
	read1=read[0] #Byte 1
	read2=read[1] #Byte 2
	read3=read[2] #Byte 3 (Changes based on button being pressed)
	read4=read[3] #Byte 4
	read5=read[4] #Byte 5
	read6=read[5] #Byte 6 (Changes when touch/proximity is detected)
	if read6==0:
		touch=-1
		prev=-1
		read3=-1
	touchbit = read6 & 0x01
	#if read6>=1 and read3!=prev and touch==-1:
	if touchbit == 1 and read3!=prev:
		prev=read3
		touchbit=-1
		touch=1
		if read3==0:
			print"Button 1 was pressed"
		elif read3==1:
			print"Button 2 was pressed"
		elif read3==2:
			print"Button 3 was pressed"
		elif read3==3:
			print"Button 4 was pressed"
		elif read3==4:
			print"Button 5 was pressed"
		elif read3==5:
			print"Button 6 was pressed"
		elif read3==6:
			print"Button 7 was pressed"
		elif read3==7:
			print"Button 8 was pressed"
		elif read3==8:
			print"Button 9 was pressed"
		elif read3==9:
			print"Button 10 was pressed"
		elif read3==10:
			print"Button 11 was pressed"
		elif read3==11:
			print"Button 12 was pressed"
		elif read3==12:
			print"Button 13 was pressed"
		elif read3==13:
			print"Button 14 was pressed"
		elif read3==14:
			print"Button 15 was pressed"
		elif read3==15:
			print"Button 16 was pressed"




