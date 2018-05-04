#!/usr/bin/python

from smbus2 import SMBus
import time
import math

busnum = 1
opt1 = 0x44		#i2c address for light sensor
evm_address = 0x1b	#i2c address for 4710 EVM

config = 0x10c4		#configuration byte for light sensor register 0x01

#list of registers on 4710 EVM
rw_reg1 = 0x36
rw_reg2 = 0x3a
resp_reg1 = 0x37
resp_reg2 = 0x3b

#list of opcodes for 4710 EVM
disp_size=0x13	#opcode for reading display size
write_ctrl=0x50	#opcode for writing LED output control method
read_ctrl=0x51	#opcode for reading LED output control method
write_en=0x52	#opcode for writing RGB LED enable
read_en=0x53	#opcode for reading RGB LED enable
write_led=0x54	#opcode for writing RGB LED currents
read_led=0x55	#opcode for read RGB LED currents


bus = SMBus(busnum)
try:
	b1 = bus.write_word_data(opt1, 0x01, config)
	print(b1)
except IOError:
	print("light sensor disconnected")
bus.close()

led_min = 91
r_max = 736
gb_max = 983

#print(led_min)
#print(led_min & 0xff)
#print(led_min >> 8)

r = led_min
gb = led_min

iterations = 16
step1 = int( math.floor((r_max-led_min)/(iterations-1)) )
step2 = int( math.floor((gb_max-led_min)/(iterations-1)) )
#print(step1)
#print(step2)

delay = 0.01

bus = SMBus(busnum)
for i in range(16):
	r = led_min + i*step1
	gb = led_min + i*step2
	current_list = [ r & 0xff, r>>8, gb & 0xff, gb>>8, gb & 0xff, gb>>8]
	print("currents are:\n")
	print(current_list)
	write_redo = 1
	while write_redo == 1:
		read_check=1
		try:
			time.sleep(delay)
			bus.write_byte_data(evm_address, rw_reg1, write_led)
			print("write_led executed")
			time.sleep(delay)
			bus.write_i2c_block_data(evm_address, write_led, current_list)
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
		if led_currents==current_list:
			print("led currents match")
			write_redo=0
		else:
			print("led currents are mismatched; restarting loop")
			write_redo=1
	print("current write executed")
	time.sleep(3)
	light_read_redo = 1
	while light_read_redo==1:
		try:
			w1 = bus.read_word_data(opt1, 0)
			# print "data test1: ", w1, " ", hex(w1)
			w1 = format(w1, '016b')
			bin1 = w1[8:16] + w1[0:8]
			# print "data test1: ", bin1
			exp1 = int( bin1[0:4], 2 )
			lux1 = 0.01*(2**exp1)*int( bin1[4:16], 2)
			print("data test1: ", lux1)
			light_read_redo = 0
		except IOError:
			print("light sensor reading error, restarting loop")
			light_read_redo = 1
	print("\n\n\n")


bus.close()