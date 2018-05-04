#!/usr/bin/python

from smbus2 import SMBus
import time

evm_address = 0x1b
busnum = 1
rw_reg1 = 0x36
rw_reg2 = 0x3a
resp_reg1 = 0x37
resp_reg2 = 0x3b

#list of opcodes
disp_size=0x13	#opcode for reading display size
write_ctrl=0x50	#opcode for writing LED output control method
read_ctrl=0x51	#opcode for reading LED output control method
write_en=0x52	#opcode for writing RGB LED enable
read_en=0x53	#opcode for reading RGB LED enable
write_led=0x54	#opcode for writing RGB LED currents
read_led=0x55	#opcode for read RGB LED currents

bus = SMBus(busnum)
go = 1
while go==1:
	try:
		time.sleep(0.01)
		bus.write_byte_data(evm_address, rw_reg1, read_led)
		print("read_led executed")
		time.sleep(0.01)
		bus.write_byte_data(evm_address, read_led, 0x00)
		print("write zeros to read_led executed")
		time.sleep(0.01)
		data = bus.read_i2c_block_data(evm_address, resp_reg1, 6)
		print("current read executed")
		print(data)
		go = 0
	except IOError:
		print("starting over")
bus.close()