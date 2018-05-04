#!/usr/bin/python

from smbus2 import SMBus
import time
import math

busnum = 1
ambient_sense = 0x44        #i2c address for ambient light sensor
evm_sense = 0x45        #i2c address for evm light sensor
evm_address = 0x1b    #i2c address for 4710 EVM

config = 0x10c4        #configuration byte for light sensor register 0x01

#list of registers on 4710 EVM
rw_reg1 = 0x36
rw_reg2 = 0x3a
resp_reg1 = 0x37
resp_reg2 = 0x3b

#list of opcodes for 4710 EVM
disp_size=0x13    #opcode for reading display size
write_ctrl=0x50    #opcode for writing LED output control method
read_ctrl=0x51    #opcode for reading LED output control method
write_en=0x52    #opcode for writing RGB LED enable
read_en=0x53    #opcode for reading RGB LED enable
write_led=0x54    #opcode for writing RGB LED currents
read_led=0x55    #opcode for read RGB LED currents

#autobrightness variables
ambientinput_old=2
user_brightness_old=5

bus = SMBus(busnum)


#functions
#----------------------------------------------------------------------------------
#define current reading function
def read_currents(delay, evm, rw_reg):
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
def write_currents(delay, evm, current_list, rw_reg):
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
		led_currents = read_currents(delay, evm, rw_reg)
		if led_currents==current_list:
			print("led currents match")
			write_redo=0
		else:
			print("led currents are mismatched; restarting loop")
			write_redo=1
	print("current write executed")
	return;
#----------------------------------------------------------------------------------
#define function for reading chromium debug file to get user brightness setting
#since arguments are given default values, function can be called with no arguments
def bright_read(debug_file_path = "/home/pi/bin/chrome-debug/chrome_debug.log"):
	#read all text in file then close file
	#should help avoid problem of file being written by UI while file text is
	#being analyzed
	file = open(debug_file_path, 'r') #define file to be read-only
	text = file.readlines()
	file.close()
	brightness = 0
	#create search string variable(s) to find desired data from file
	search_str = 'brightness: '
	shift = len(search_str)
	for line in text:
		if search_str in line:
			start = line.find(search_str)
			end = line.find('"',start)
			brightness = line[start+shift:end]
	return int(brightness);
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
#define light sensor configuration
def sensor_config(opt_addr):
	config = 0x10c4
	try:
		b1 = bus.write_word_data(opt_addr, 0x01, config)
		#print(b1)
		print("Sensor configuration executed on address "+hex(opt_addr) )
	except IOError:
		print("Configuration failed on address"+hex(opt_addr)+". Check light sensor connection.")
	return;
#----------------------------------------------------------------------------------
#define LED current list creating function
def set_currents(r, g, b):
	currents = [ r & 0xff, r>>8, g & 0xff, g>>8, b & 0xff, b>>8]
	return currents;
#----------------------------------------------------------------------------------
#user brightness function
def autobrightness(delay, ambientinput_old, user_brightness_old, evm_address, ambient_address, rw_reg):

	delta=0.1	#minimum percentage change, as a decimal, in ambient light level for changes to be made
	global amb_thresh

	# read user brightness setting from folder
	user_brightness = bright_read()
	print("user brightness is "+str(user_brightness) )
	if user_brightness != user_brightness_old:
		amb_thresh = light_read(delay, ambient_address)	#update the ambient lux threshold when user brightness is adjusted
	
	#Red LED Max Brightness
        red_max = 736

	#Blue LED Max Brightness
        blue_max = 983

	#Green LED Max Brightness
        green_max = 983

	#LED Currents Min
        min_current = 91

	# get light sensor reading
	ambientinput = light_read(delay, ambient_address)	

	#find what would normally be the typical rgb LED current values for the given user brightness setting
	r_norm = math.floor(min_current + float(user_brightness)/100*(red_max-min_current))
	g_norm = math.floor(min_current + float(user_brightness)/100*(green_max-min_current))
	b_norm = math.floor(min_current + float(user_brightness)/100*(blue_max-min_current))
	print("r_norm = " + str(r_norm))
	print("g_norm = " + str(g_norm))
	print("b_norm = " + str(b_norm))

	#determine if discernable change in ambient input
	if ambientinput>=ambientinput_old*(1+delta) or ambientinput<ambientinput_old*(1-delta) or user_brightness!=user_brightness_old:
		#create the current ranges for each level
		#create an adjustment for the brightness based on the log10 of the ratio of the current ambient reading and threshold reading
		adjustment = math.log10(ambientinput/amb_thresh)
		if adjustment > 1:
			adjustment = 1
		elif adjustment < -1:
			adjustment = -1
		print("adjustment is " + str(adjustment) )
		R = int( round(r_norm*(1+adjustment), 0) )
		G = int( round(g_norm*(1+adjustment), 0) )
		B = int( round(b_norm*(1+adjustment), 0) )
		if R > red_max:
			R = red_max
		elif R < min_current:
			R = min_current
		if G > green_max:
			G = green_max
		elif G < min_current:
			G = min_current
		if B > blue_max:
			B = blue_max
		elif B < min_current:
			B = min_current
		
		print("Red LED is "+ str(R) )
		print("Green LED is "+ str(G) )
		print("Blue Value is "+ str(B) )
		#Read current values, if match, end, if not match, change
	
		current_list = set_currents(R, G, B)
		led_currents = read_currents(delay, evm_address, rw_reg)
		if current_list != led_currents:
			write_currents(delay, evm_address, current_list, rw_reg)
	ambientinput_old=ambientinput
	user_brightness_old=user_brightness
	return [ambientinput_old, user_brightness_old];
#----------------------------------------------------------------------------------

sensor_config(evm_sense)
sensor_config(ambient_sense)

#get the initial ambient light reading on initialization to use as initial threshold for determining if changes should be made
amb_thresh = light_read(0.1, ambient_sense)

temp = [ambientinput_old, user_brightness_old]
try:
	while True:
		temp = autobrightness(0.1, temp[0], temp[1], evm_address, ambient_sense, rw_reg1)
		print("\n\n\n")
		time.sleep(3)
except KeyboardInterrupt:
	bus.close()