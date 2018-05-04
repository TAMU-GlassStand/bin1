#!/usr/bin/python

from smbus2 import SMBus
import time
import math

#define current writing function
#define current reading function
def read_currents(delay, evm):
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
#----------------------------------------------------------------------------------
#define current writing function
def write_currents(delay, evm, current_list):
	rw_reg = 0x36		#address of the read/write register on the EVM
	write_led = 0x54	#opcode to write the LED currents
	#current_list is a 6 element list with the least significant and then most significant bytes of each color LED, red, green ,and blue
	write_redo = 1	#continue the write_led current loop if anything fails
	while write_redo == 1:
		try:
			time.sleep(delay)
			bus.write_byte_data(evm, rw_reg, write_led)
			print("write_led executed")
			time.sleep(delay)
			bus.write_i2c_block_data(evm, write_led, current_list)
			print("write currents executed")
			time.sleep(delay)
			write_redo=0
		except IOError:
			print("restarting current write loop")
			continue
		led_currents = read_currents(delay, evm)
		if led_currents==current_list:
			print("led currents match")
			write_redo=0
		else:
			print("led currents are mismatched; restarting loop")
			write_redo=1
	print("current write executed")
	return;
#----------------------------------------------------------------------------------
#define light sensor reading function
def light_read(delay, opt_address):
	light_read_redo = 1
	while light_read_redo==1:
		try:
			time.sleep(delay)
			data = bus.read_word_data(opt_address, 0)
			# print("data test1: "+data+" "+hex(data) )
			data = format(data, '016b')
			bin = data[8:16] + data[0:8]
			# print("data test "+hex(opt_address)+": "+bin)
			exp = int( bin[0:4], 2 )
			lux = 0.01*(2**exp)*int( bin[4:16], 2)
			print("data test "+hex(opt_address)+": "+ str(lux) )
			light_read_redo = 0
		except IOError:
			print("light sensor reading error, restarting loop")
			light_read_redo = 1
	return lux;
#----------------------------------------------------------------------------------




busnum = 1
opt1 = 0x44		#i2c address for light sensor
opt2 = 0x45		#i2c address for second light sensor
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

sensor = opt2
bus = SMBus(busnum)
try:
	b1 = bus.write_word_data(sensor, 0x01, config)
	print(b1)
	print("sensor configuration executed on address "+hex(sensor) )
except IOError:
	print("light sensor disconnected")
bus.close()
time.sleep(3)

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
print(step1)
print(step2)
time.sleep(3)

delay = 0.1
delay2 = 1
delay3 = 0.1

#define output file for data collection
output = open('/home/pi/bin/brightness_data_20inches.txt', 'w')
#create file header
output.write("loop"+"\t\t"+"red"+"\t\t"+"green"+"\t\t"+"blue"+"\t\t"+"sensor\n")


bus = SMBus(busnum)
for i in range(iterations+1):
	r = led_min + i*step1
	gb = led_min + i*step2
	if r > r_max:
		r = r_max
	if gb > gb_max:
		gb = gb_max
	current_list = [ r & 0xff, r>>8, gb & 0xff, gb>>8, gb & 0xff, gb>>8]
	print("currents are:")
	print(current_list)
	write_currents(delay, evm_address, current_list)
	time.sleep(delay2)
	lux1 = light_read(delay3, opt2)
	lux2 = light_read(delay3, opt2)
	lux3 = light_read(delay3, opt2)
	avg = (lux1 + lux2 + lux3)/3
	output.write(str(i)+"\t\t"+str(r)+"\t\t"+str(gb)+"\t\t"+str(gb)+"\t\t"+str(avg)+"\n")
	time.sleep(delay2)
	print("\n\n\n")

output.close()
bus.close()