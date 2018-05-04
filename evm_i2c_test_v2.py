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

write=1

if write==0:
	bus = SMBus(busnum)
	
	bus.close()
else:
	bus = SMBus(busnum)
	currents_max = [ 0xe0, 0x02, 0xd7, 0x03, 0xd7, 0x03 ]
	currents_mid = [ 0x44, 0x01, 0x44, 0x01, 0x44, 0x01 ]
	currents_min = [ 0x91, 0x00, 0x91, 0x00, 0x91, 0x00 ]
	
	switch = currents_mid
	w_loops = 0
	while w_loops<100:
		try:
			time.sleep(3)
			bus.write_byte_data(evm_address, rw_reg1, write_led)
			print("write_led executed")
			time.sleep(3)
			bus.write_i2c_block_data(evm_address, write_led, currents_min)
			print("write currents executed")
			w_loops=101
		except IOError:
			print("write loop1 run failed")
			w_loops=w_loops+1
			#time.sleep(1)
		try:
			time.sleep(3)
			#bus.write_byte_data(evm_address, rw_reg1, write_led)
			print("write_led executed")
			time.sleep(3)
			bus.write_i2c_block_data(evm_address, write_led, currents_mid)
			print("write currents executed")
			w_loops=101
		except IOError:
			print("write loop2 run failed")
			w_loops=w_loops+1
			#time.sleep(1)
		try:
			time.sleep(3)
			#bus.write_byte_data(evm_address, rw_reg1, write_led)
			print("write_led executed")
			time.sleep(3)
			bus.write_i2c_block_data(evm_address, write_led, currents_max)
			print("write currents executed")
			w_loops=101
		except IOError:
			print("write loop3 run failed")
			w_loops=w_loops+1
			#time.sleep(1)

	if w_loops==100:
		print("all write loops failed")
	r_loops = 0
	while r_loops<100:
		try:
			time.sleep(3)
			bus.write_byte_data(evm_address, rw_reg1, read_led)
			print("read_led executed")
			time.sleep(3)
			bus.write_byte_data(evm_address, read_led, 0x00)
			print("write zeros to read_led executed")
			time.sleep(3)
			data = bus.read_i2c_block_data(evm_address, resp_reg1, 16)
			print("current read executed")
			print(data)
			r_loops=101
		except IOError:
			print("read loop run failed")
			r_loops=r_loops+1
			#time.sleep(1)

	if r_loops==100:
		print("all read loops failed")
	print("all loops exited")
	
	bus.close()