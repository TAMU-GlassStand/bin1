#!/usr/bin/python

from smbus2 import SMBus
import time

#define current reading function
def read_currents(bus, delay, evm):
	rw_reg = 0x36	#address of the read/write register on the EVM
	read_led = 0x55	#opcode to read the LED currents
	resp_reg = 0x37	#address of the read response register on the EVM
	success = 0	#keep track of whether the read was successful
	loop_count = 0	#keep track of how many failed loops have occured
	while success==0:
		try:
			time.sleep(delay)
			bus.write_byte_data(evm, rw_reg, read_led)
			print("read_led executed")
			time.sleep(delay)
			bus.write_byte_data(evm, read_led, 0x00)
			print("write zeros to read_led executed")
			time.sleep(delay)
			led_currents = bus.read_i2c_block_data(evm, resp_reg, 6)
			print("current read executed")
			print(led_currents)
			success = 1
		except IOError:
			if loop_count<150:
				print("starting over")
			else:
				print("Too many failed loops. Check that EVM is connected.")
				break
	return led_currents;


bus = SMBus(1)
currents = read_currents(bus, 0.1, 0x1b)
print(currents)