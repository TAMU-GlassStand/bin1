#!/usr/bin/python

from smbus2 import SMBus
from smbus2 import SMBusWrapper
import time

evm_address = 0x1b
busnum = 1
rw_reg1 = 0x36		#read request and write register address
rw_reg2 = 0x3a		#read request and write register other address
resp_reg1 = 0x37	#read response register address
resp_reg2 = 0x3b	#read response register other address

#list of opcodes
disp_size=0x13	#opcode for reading display size
write_ctrl=0x50	#opcode for writing LED output control method
read_ctrl=0x51	#opcode for reading LED output control method
write_en=0x52	#opcode for writing RGB LED enable
read_en=0x53	#opcode for reading RGB LED enable
write_led=0x54	#opcode for writing RGB LED currents
read_led=0x55	#opcode for read RGB LED currents

write=0

if write==0:
	bus = SMBus(busnum)
	try:
		bus.write_byte_data(evm_address, rw_reg1, write_en)
		time.sleep(1)
		bus.write_byte_data(evm_address, write_en, 7)
	except IOError:
		print("write instructions failed")
		try:
			bus.write_byte_data(evm_address, rw_reg1, write_en)
			print("write_en executed")
			time.sleep(1)
			bus.write_byte_data(evm_address, write_en, 4)
		except IOError:
			print("write instruction failed again")
	time.sleep(1)
	try:
		#bus.write_byte_data(evm_address, rw_reg1, read_en)
		#time.sleep(1)
		data = bus.read_byte_data(evm_address, read_en)
		print("read executed")
		print(data)
		time.sleep(1)
		data2 = bus.read_byte_data(evm_address, disp_size)
		print(data2)
	except IOError:
		print("read from response register failed")
		try:
			#bus.write_byte_data(evm_address, rw_reg1, read_en)
			time.sleep(1)
			data = bus.read_byte_data(evm_address, read_en)
			time.sleep(1)
			data2 = bus.read_byte_data(evm_address, disp_size)
			print(data)
			print(data2)
		except IOError:
			print("read from response register failed again")
	bus.close()
else:
	bus = SMBus(busnum)
	currents_max = [ 0xe0, 0x02, 0xd7, 0x03, 0xd7, 0x03 ]
	currents_mid = [ 0x44, 0x01, 0x44, 0x01, 0x44, 0x01 ]
	currents_min = [ 0x91, 0x00, 0x91, 0x00, 0x91, 0x00 ]
	switch = currents_max
	try:
		bus.write_byte_data(evm_address, rw_reg1, write_led)
		print("write_led executed")
		time.sleep(1)
		#for i in range(6):
		bus.write_i2c_block_data(evm_address, rw_reg2, switch)
		print("write currents executed")
	except IOError:
		print("one of the write commands failed")
		time.sleep(1)
		try:
			bus.write_byte_data(evm_address, rw_reg1, write_led)
			print("second write_led executed")
			time.sleep(1)
			bus.write_i2c_block_data(evm_address, write_led, switch)
			print("second write currents executed")
		except IOError:
			print("another one of the write commands failed")
	time.sleep(1)
	
	try:
		bus.write_byte_data(evm_address, rw_reg1, read_led)
		print("read_led exectued")
		time.sleep(1)
		data = bus.read_i2c_block_data(evm_address, resp_reg1, 6)
		print("current read executed")
		print(data)
	except IOError:
		print("first set of write/read failed")
	time.sleep(1)
	try:
		bus.write_byte_data(evm_address, rw_reg1, read_led)
		print("read_led2 exectued")
		time.sleep(1)
		data = bus.read_i2c_block_data(evm_address, resp_reg2, 6)
		print("current read2 executed")
		print(data)
	except IOError:
		print("second set of write/read failed")
	bus.close()