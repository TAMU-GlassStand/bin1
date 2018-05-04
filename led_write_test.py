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

currents_max = [ 0xe0, 0x02, 0xd7, 0x03, 0xd7, 0x03 ]
currents_mid = [ 0x44, 0x01, 0x44, 0x01, 0x44, 0x01 ]
currents_min = [ 0x5b, 0x00, 0x5b, 0x00, 0x5b, 0x00 ]
currents_rand= [ 0xa2, 0x01, 0xa2, 0x01, 0xa2, 0x01 ]
current_choice = currents_mid

delay = 0.01

bus = SMBus(busnum)
read_check = 1	#continue the read_led checking loop if anything fails
write_redo = 1	#continue the write_led current loop if anything fails

while write_redo==1:
	read_check=1
	try:
		time.sleep(delay)
		bus.write_byte_data(evm_address, rw_reg1, write_led)
		print("write_led executed")
		time.sleep(delay)
		bus.write_i2c_block_data(evm_address, write_led, current_choice)
		print("write currents executed")
		time.sleep(delay)
		write_redo=0
	except IOError:
		print("restarting current write loop")
		continue
	while read_check==1:
		try:
			time.sleep(delay)
			bus.write_byte_data(evm_address, rw_reg1, read_led)
			print("read_led executed")
			time.sleep(delay)
			bus.write_byte_data(evm_address, read_led, 0x00)
			print("write zeros to read_led executed")
			time.sleep(delay)
			led_currents = bus.read_i2c_block_data(evm_address, resp_reg1, 6)
			print("current read executed")
			print(led_currents)
			read_check = 0
		except IOError:
			print("starting over")
	if led_currents==current_choice:
		print("led currents match")
		write_redo=0
	else:
		print("led currents are mismatched; restarting loop")
		write_redo=1


bus.close()