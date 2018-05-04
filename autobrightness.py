#!/usr/bin/python

from smbus2 import SMBus
import time
import math

#functions
#define current reading function
def read_currents(bus, delay, evm, rw_reg):
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
def write_currents(bus, delay, evm, current_list, rw_reg):
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
		led_currents = read_currents(bus, delay, evm, rw_reg)
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
def light_read(bus, delay, opt_address):
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


busnum = 1
opt1 = 0x44        #i2c address for light sensor
opt2 = 0x45        #i2c address for second light sensor
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


#user brightness function
def autobrightness(bus, ambientinput_old, user_brightness_old, rw_reg):


	step_Number=20
	delta=5
#Red LED Max Brightness
        RedAbsMax = 736

#Blue LED Max Brightness
        BlueAbsMax = 983

#Green LED Max Brightness
        GreenAbsMax = 983

#LED Currents Min
        AbsMin = 91

#Define RedAutoMinLower
        RedAutoMinLower = (RedAbsMax- AbsMin)/2 + AbsMin

#Define GreenAutoMinLower
        GreenAutoMinLower = (GreenAbsMax - AbsMin)/2 + AbsMin

#Define BlueAutoMinLower
        BlueAutoMinLower = (BlueAbsMax - AbsMin)/2 + AbsMin

#stepSize
        RedstepSize = (RedAbsMax - AbsMin)/step_Number
        GreenstepSize = (GreenAbsMax - AbsMin)/step_Number
        BluestepSize = (BlueAbsMax - AbsMin)/step_Number

# get light sensor reading
	ambientinput = light_read(bus, 0.1, opt1)

# read user brightness setting from folder
	user_brightness= bright_read()
	print("user brightness is "+str(user_brightness) )
	user_brightness = user_brightness/10

#determine if dercinible change in ambient input
	if any([ambientinput>=ambientinput_old-delta, ambientinput< ambientinput_old + delta, user_brightness != user_brightness_old]):
#Setting the Lower Bound of AutoBrightness
		if ambientinput > 100:
			step = 9
		elif ambientinput >= 90:
			step = 8
		elif ambientinput >= 80:
			step = 7
		elif ambientinput >= 70:
			step = 6
		elif ambientinput >= 60:
			step = 5
		elif ambientinput >= 50:
			step = 4
		elif ambientinput >= 40:
			step = 3
		elif ambientinput >= 30:
			step = 2
		elif ambientinput >= 20:
			step = 1
		else:
			step = 0

        print(step)
	print(step)
	if step == 9:
		setR = RedAutoMinLower
		setG = GreenAutoMinLower
		setB = BlueAutoMinLower
	
	if step == 8:
		setR = RedAutoMinLower - RedstepSize
		setG = GreenAutoMinLower - GreenstepSize
		setB = BlueAutoMinLower - BluestepSize
	
	if step == 7:
		setR = RedAutoMinLower - 2*RedstepSize
		setG = GreenAutoMinLower - 2*GreenstepSize
		setB = BlueAutoMinLower - 2*BluestepSize
	
	if step == 6:
		setR = RedAutoMinLower - 3*RedstepSize
		setG = GreenAutoMinLower - 3*GreenstepSize
		setB = BlueAutoMinLower - 3*BluestepSize
	
	if step == 5:
		setR = RedAutoMinLower - 4*RedstepSize
		setG = GreenAutoMinLower - 4*GreenstepSize
		setB = BlueAutoMinLower - 4*BluestepSize
	
	if step == 4:
		setR = RedAutoMinLower - 5*RedstepSize
		setG = GreenAutoMinLower - 5*GreenstepSize
		setB = BlueAutoMinLower - 5*BluestepSize
	
	if step == 3:
		setR = RedAutoMinLower - 6*RedstepSize
		setG = GreenAutoMinLower - 6*GreenstepSize
		setB = BlueAutoMinLower - 6*BluestepSize
	
	if step == 2:
		setR = RedAutoMinLower - 7*RedstepSize
		setG = GreenAutoMinLower - 7*GreenstepSize
		setB = BlueAutoMinLower - 7*BluestepSize
	
	if step == 1:
		setR = RedAutoMinLower - 8*RedstepSize
		setG = GreenAutoMinLower - 8*GreenstepSize
		setB = BlueAutoMinLower - 8*BluestepSize
	
	if step == 0:
		setR = RedAutoMinLower - 9*RedstepSize
		setG = GreenAutoMinLower - 9*GreenstepSize
		setB = BlueAutoMinLower - 9*BluestepSize
	
	print("step Value is "+ str(step) )
	print("Red LED is "+ str(setR) )
	print("Green LED is "+ str(setG) )
	print("Blue Value is "+ str(setB) )
	#determine current values based on min brightness and user brightness setting
	R=setR+user_brightness*RedstepSize
	B=setB+user_brightness*BluestepSize
	G=setG+user_brightness*GreenstepSize
	#Read current values, if match, end, if not match, change
	current_list = [ R & 0xff, R>>8, B & 0xff, B>>8, G & 0xff, G>>8]
	led_currents = read_currents(bus, 0.1, evm_address, rw_reg)
	if current_list != led_currents :
		write_currents(bus, 0.1, evm_address, current_list, rw_reg)
	ambientinput_old=ambientinput
	user_brightness_old=user_brightness
	return [ambientinput_old, user_brightness_old];
	
bus = SMBus(busnum)
temp = [ambientinput_old, user_brightness_old]
try:
	while True:
		temp = autobrightness(bus, temp[0], temp[1], rw_reg1)
		print("\n\n\n")
		time.sleep(3)
except KeyboardInterrupt:
	bus.close()