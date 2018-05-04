#!/usr/bin/python

from smbus2 import SMBus
import time
import math

#define current writing function
def write_currents (delay, current_list):
	#current_list is a 6 element list with the least significant and then most significant bytes of each color LED, red, green ,and blue
	write_redo = 1	#continue the write_led current loop if anything fails
	while write_redo == 1:
		read_check=1	#continue the read_led checking loop if anything fails
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
	return;




busnum = 1
evm_address = 0x1b
opt1 = 0x44

#list of registers on 4710 EVM
rw_reg1 = 0x36
rw_reg2 = 0x3a
resp_reg1 = 0x37
resp_reg2 = 0x3b

config = 0x10c4	#configuration bytes for opt register 0x01

#list of opcodes
disp_size=0x13	#opcode for reading display size
write_ctrl=0x50	#opcode for writing LED output control method
read_ctrl=0x51	#opcode for reading LED output control method
write_en=0x52	#opcode for writing RGB LED enable
read_en=0x53	#opcode for reading RGB LED enable
write_led=0x54	#opcode for writing RGB LED currents
read_led=0x55	#opcode for read RGB LED currents

#some LED current values for the 4710 EVM
currents_max = [ 0xe0, 0x02, 0xd7, 0x03, 0xd7, 0x03 ]
currents_mid = [ 0x44, 0x01, 0x44, 0x01, 0x44, 0x01 ]
currents_min = [ 0x5b, 0x00, 0x5b, 0x00, 0x5b, 0x00 ]
#currents_rand= [ 0xa2, 0x01, 0xa2, 0x01, 0xa2, 0x01 ]
led_min = 91	#minimum LED current as an integer
r_max = 736	#maximum red LED current as an integer
gb_max = 983	#maximum green and blue LED current as an integer

delay = 0.001
delay2 = 0.1

#write configuration bytes to the opt3001 sensor
bus = SMBus(busnum)
try:
	b1 = bus.write_byte_data(opt1, 0x01, config)
	print(b1)
except IOError:
	print("light sensor disconnected")
bus.close()

iterations = 80
step_r = int( math.floor((r_max-led_min)/(iterations-1)) )
step_gb = int( math.floor((gb_max-led_min)/(iterations-1)) )
print(step_r)
print(step_gb)
#initialize all LED currents to minimum value
r = led_min
g = led_min
b = led_min
time.sleep(3)

bus = SMBus(busnum)
#set LED currents to minimum values
current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
write_currents(delay, current_list )
print("\n\n\n")
#loop for increasing red LED current (red alone at max)
for i in range(iterations):
	r = led_min + i*step_r
	#g = led_min + i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for increasing green LED current (red and green at max)
for i in range(iterations):
	#r = led_min + i*step_r
	g = led_min + i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for decreasing red LED current (green alone at max)
for i in range(iterations):
	r = r_max - i*step_r
	#g = led_min + i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for increasing blue LED current (green and blue at max)
for i in range(iterations):
	#r = led_min + i*step_r
	#g = led_min + i*step_gb
	b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for decreasing green LED current (blue alone at max)
for i in range(iterations):
	#r = led_min + i*step_r
	g = gb_max - i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for increasing red LED current (blue and red at max)
for i in range(iterations):
	r = led_min + i*step_r
	#g = led_min + i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)
#loop for increasing green LED current (red, green, and blue at max)
for i in range(iterations):
	#r = led_min + i*step_r
	g = led_min + i*step_gb
	#b = led_min + i*step_gb
	current_list = [r & 0xff, r >> 8, g & 0xff, g >> 8, b & 0xff, b >> 8]
	write_currents(delay, current_list)
	print("\n\n\n")
	time.sleep(delay2)

bus.close()



