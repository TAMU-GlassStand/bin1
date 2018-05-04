#!/usr/bin/python

from smbus2 import SMBus
import RPi.GPIO as gpio
from pykeyboard import PyKeyboard
import time
import math
from subprocess import call

#clear any previous gpio pin setups
gpio.cleanup()

#setup gpio pins to be defined based on their pin number on the gpio header
gpio.setmode(gpio.BOARD)

#define variables used for keyboard and mouse navigations
prev=-1
file_sel=-1
user_location=-1 # Used to determine where the user is: 0=Settings, 1=Google Drive, 2=Removeable Storage
pdf_view=-1 	 # Used to determine how the pdf is being displayed: 0=???, 1=Google Drive Preview, 2=Chrome Viewer
enter_count=0


#Google Drive Variables
n_pdf=0

# Removable Storage Variables
n_usb=0

#lux threshold for identifying whether the projector is turned on or off
lux_thresh = 150

#define functions for use in the script
#----------------------------------------------------------------------------------
#define function for configuring EVM projector output to rear projection mode
def evm_config(bus, delay, evm, rw_reg, resp_reg):
	write_orient=0x14	#opcode for writing image orientation
	read_orient=0x15	#opcode for reading image orientation
	orientation=0x02	#hex code for image flip across vertical axis
	success = 0	#keep track of whether the write was successful
	read_redo = 1	#keep track of whether reading back of data was successful
	while success==0:
		try:
			time.sleep(delay)
			bus.write_byte_data(evm, rw_reg, write_orient)
			print("write_orient executed")
			time.sleep(delay)
			bus.write_byte_data(evm, write_orient, orientation)
			print("orientation flip written to EVM")
			time.sleep(delay)
		except IOError:
			print("restarting orientation write loop")
		while read_redo == 1:
			try:
				time.sleep(delay)
				bus.write_byte_data(evm, rw_reg, read_orient)
				print("read_orient executed")
				time.sleep(delay)
				bus.write_byte_data(evm, read_orient, 0x00)
				print("write zeros to read_orient executed")
				time.sleep(delay)
				orient_read = bus.read_byte_data(evm, resp_reg)
				print("read orientation data executed")
				read_redo = 0
			except IOError:
				print("restarting orientation read loop")
		if orient_read == orientation:
			success = 1
		else:
			print("orientation mismatch; restarting loop")
			success = 0
			
	return;
#----------------------------------------------------------------------------------
#define current reading function
def read_currents(bus, delay, evm, rw_reg, resp_reg):
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
def write_currents(bus, delay, evm, current_list, rw_reg, resp_reg):
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
		led_currents = read_currents(bus, delay, evm, rw_reg, resp_reg)
		if led_currents==current_list:
			print("led currents match")
			write_redo=0
		else:
			print("led currents are mismatched; restarting loop")
			write_redo=1
	print("current write executed")
	return;
#----------------------------------------------------------------------------------
#define light sensor configuration
def sensor_config(bus, opt_addr):
	config = 0x10c4
	try:
		b1 = bus.write_word_data(opt_addr, 0x01, config)
		#print(b1)
		print("Sensor configuration executed on address "+hex(opt_addr) )
	except IOError:
		print("Configuration failed on address"+hex(opt_addr)+". Check light sensor connection.")
	return;
#----------------------------------------------------------------------------------
#define light sensor reading function
def light_read(bus, delay, opt_addr):
	light_read_redo = 1
	while light_read_redo==1:
		try:
			time.sleep(delay)
			data = bus.read_word_data(opt_addr, 0)
			# print("data test1: "+data+" "+hex(data) )
			data = format(data, '016b')
			bin = data[8:16] + data[0:8]
			# print("data test "+hex(opt_addr)+": "+bin)
			exp = int( bin[0:4], 2 )
			lux = 0.01*(2**exp)*int( bin[4:16], 2)
			print("data test "+hex(opt_addr)+": "+ str(lux) )
			light_read_redo = 0
		except IOError:
			print("light sensor reading error, restarting loop")
			light_read_redo = 1
	return lux;
#----------------------------------------------------------------------------------
#define LED current list creating function
def set_currents(r, g, b):
	currents = [ r & 0xff, r>>8, gb & 0xff, gb>>8, gb & 0xff, gb>>8]
	return currents;
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
#define function for turning projector on or off (like hitting the pushbutton switch)
#the gpio pin controlling the pin needs to fall LOW for at least 300ms
def projector_switch(channel):
	gpio.output(channel, gpio.HIGH)
	time.sleep(0.1)
	gpio.output(channel, gpio.LOW)
	time.sleep(0.4)
	gpio.output(channel, gpio.HIGH)
	return;
#----------------------------------------------------------------------------------
#define function for checking light sensor and turning projector off
#lux_thresh is the lux measurement, as measured by the light sensor, over which the
#projector evm is assumed to be projecting an image; the projector is assumed to be
#on as though the pushbutton were pressed after 
def projector_off(bus, delay, evm_sensor, gpio_channel):
	lux = light_read(bus, delay, evm_sensor)
	if lux>=lux_thresh:	#evm is on, so turn it off
		projector_switch(gpio_channel)
	return;
#----------------------------------------------------------------------------------
#define function for checking light sensor and turning projector on
#lux_thresh is the lux measurement, as measured by the light sensor, over which the
#projector evm is assumed to be projecting an image; the projector is assumed to be
#on as though the pushbutton were pressed after 
def projector_on(bus, delay, evm_sensor, gpio_channel):
	lux = light_read(bus, delay, evm_sensor)
	if lux<lux_thresh:	#evm is off, so turn it on
		projector_switch(gpio_channel)
	return;
#----------------------------------------------------------------------------------
#define user interface startup function
def start_UI(m, k):
	k.press_key(k.shift_key)
	k.press_key(k.alt_key)
	k.tap_key('t')
	k.release_key(k.shift_key)
	k.release_key(k.alt_key)	
	return;
#----------------------------------------------------------------------------------
#define function for closing all windows in user interface
def close_window(m, k):
	k.press_key(k.alt_key)
	k.tap_key(k.function_keys[4])
	k.release_key(k.alt_key)	
	return;
#----------------------------------------------------------------------------------
#define setttings button
def settings_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	m.move(x_pos*9, y_pos*15)
	m.click(x_pos*9, y_pos*15, 1)
	user_location=0	#Flag so buttons 2 and 3 only click if on the settings page		

	#Clear scrolling count
	n_usb=0
	n_pdf=0
	return;
#----------------------------------------------------------------------------------
#define google drive button
def google_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	# Google Drive
	m.move(x_pos*9, y_pos*45)
	m.click(x_pos*9, y_pos*45, 1)
	user_location=1
	time.sleep(1)
	k.tap_key(k.tab_key, 3)

	#Clear scrolling count
	n_usb=0
	n_pdf=0
	return;
#----------------------------------------------------------------------------------
#define removable storage button
def removable_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	m.move(x_pos*9, y_pos*80)
	m.click(x_pos*9, y_pos*80)
	user_location=2
	time.sleep(1)
	k.tap_key(k.tab_key)

	#Clear scrolling count
	n_usb=0
	n_pdf=0
	return;
#----------------------------------------------------------------------------------
#define brightness increase button
def bright_up(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==0:
		# Brightness Plus
		m.move(x_pos*30, y_pos*21.25)
		m.click(x_pos*30, y_pos*21.25, 1)

		# Apply Changes  
		m.move(x_pos*26, y_pos*22.5)
		m.click(x_pos*26, y_pos*22.5, 1)

		#Clear scrolling count 
		n_usb=0
		n_pdf=0
	return;
#----------------------------------------------------------------------------------
#define brightness decrease button
def bright_down(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==0:
		# Brightness Minus
		m.move(x_pos*35.25, y_pos*21.25)
		m.click(x_pos*35.25, y_pos*21.25, 1)

		# Apply Changes
		m.move(x_pos*26, y_pos*22.5)
		m.click(x_pos*26, y_pos*22.5, 1)

		#Clear scrolling count
		n_usb=0
		n_pdf=0
	return;
#----------------------------------------------------------------------------------
#define tab backward (up) button
def tab_back(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==1 and enter_count==0:
		n_pdf=n_pdf-1
		k.press_key(k.shift_key)
		k.tap_key(k.tab_key, 2)
		k.release_key(k.shift_key)
	
	elif user_location==2:
		n_usb=n_usb-1
		k.press_key(k.shift_key)
		k.tap_key(k.tab_key)
		k.release_key(k.shift_key)
	return;
#----------------------------------------------------------------------------------
#define tab forward (down) button
def tab_forward(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==1 and enter_count==0:
		n_pdf=n_pdf+1
		k.tap_key(k.tab_key, 2)

	elif user_location==2:
		n_usb=n_usb+1
		k.tap_key(k.tab_key)
	return;
#----------------------------------------------------------------------------------
#define page back button
def page_back(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==1 and enter_count==1:
		k.press_key(k.control_key)
		k.tap_key('w')
		k.release_key(k.control_key)
		enter_count=0
		
	if user_location==2:
		k.press_key(k.control_key)
		k.tap_key('w')
		k.release_key(k.control_key)
		enter_count=0
	return;
#----------------------------------------------------------------------------------
#define enter button
def enter_button(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	if user_location==1:
		k.tap_key(k.enter_key)
		enter_count=1
	
	if user_location==2:
		k.tap_key(k.enter_key)
		time.sleep(2)
		k.press_key(k.control_key)
		k.tap_key
		#pdf_view==1
	return;
#----------------------------------------------------------------------------------
#define home page button (close tab)
def home_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define zoom in button
def zoom_in(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define zoom out button
def zoom_out(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define previous page button
def prev_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define next page button
def next_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define fit to page button
def fit_page(m, k):
	x_dim, y_dim=m.screen_size()
	x_pos=x_dim/100
	y_pos=y_dim/100
	return;
#----------------------------------------------------------------------------------
#define function for reading inputs from the captivate when the gpio interrupt occurs
def read_captivate(bus, delay, address, m, k):
	data0 = [0, 0, 0, 0, 0, 0]
	try:
		bus.write_i2c_block_data(address, 0x00, data0)
		read = bus.read_i2c_block_data(address, 0x00, 6)
		#byte 3 (read[2]) changes based on button being pressed
		#byte 6 (read[5]) changes when touch/proximity is detected
		touchbit = read[5] & 0x01
	except IOError:
			
	#define button values
	start = 0
	settings = 5
	google = 9
	removable = 13
	bright_up = 2
	bright_down = 12
	tab_back_up = 8
	tab_forward_down = 11
	back = 4
	enter = 7
	home = 1
	zoom_in = 14
	zoom_out = 15
	prev_page = 6
	next_page = 3
	fit_page = 10
	
	#determine which button was pressed and call the appropriate function
	if touchbit==1:
		if read[5] == start:
			start_UI(m,k)
		elif read[5] == settings:
			settings_page(m,k)
		elif read[5] == google:
			google_page(m,k)
		elif read[5] == removable:
			removable_page(m,k)
		elif read[5] == bright_plus:
			bright_up(m,k)
		elif read[5] == bright_minus:
			bright_down(m,k)
		elif read[5] == tab_back_up:
			tab_back(m,k)
		elif read[5] == tab_forward_down:
			tab_forward(m,k)
		elif read[5] == back:
			page_back(m,k)
		elif read[5] == enter:
			enter_button(m,k)
		elif read[5] == home:
			home_page(m,k)
		elif read[5] == zoom_in:
			zoom_in(m,k)
		elif read[5] == zoom_out:
			zoom_out(m,k)
		elif read[5] == prev_page:
			prev_page(m,k)
		elif read[5] == next_page:
			next_page(m,k)
		elif read[5] == fit_page:
			fit_page(m,k)
		else
	return;
#----------------------------------------------------------------------------------
#define function for reading the gpio output(s) from the arduino
#this may also be the automatic shutdown function
def auto_shutdown(bus, delay, evm_sensor, gpio_channel):
	projector_off(bus, delay, evm_sensor, gpio_channel)
	call("sudo shutdown -h now", shell=True)
	return;
#----------------------------------------------------------------------------------

#create the keyboard and mouse objects for doing mouse and keyboard manipulations
keyboard = PyKeyboard()
mouse = PyMouse()

#define i2c bus number and i2c device addresses
busnum = 1
captivate = 0x0a
evm_address = 0x1b
amb_sense = 0x44	#address of sensor for detecting ambient light level
evm_sense = 0x45	#address of sensor for detecting projector evm light level

#list of registers on 4710 EVM
rw_reg1 = 0x36
rw_reg2 = 0x3a
resp_reg1 = 0x37
resp_reg2 = 0x3b

config = 0x10c4	#configuration bytes for opt register 0x01

#list of opcodes
disp_size=0x13	#opcode for reading display size
write_orient=0x14	#opcode for writing image orientation
read_orient=0x15	#opcode for reading image orientation
write_ctrl=0x50	#opcode for writing LED output control method
read_ctrl=0x51	#opcode for reading LED output control method
write_en=0x52	#opcode for writing RGB LED enable
read_en=0x53	#opcode for reading RGB LED enable
write_led=0x54	#opcode for writing RGB LED currents
read_led=0x55	#opcode for read RGB LED currents
read_sys=0xd1	#opcode for reading system status

#some LED current values for the 4710 EVM
#currents_max = [ 0xe0, 0x02, 0xd7, 0x03, 0xd7, 0x03 ]
#currents_mid = [ 0x44, 0x01, 0x44, 0x01, 0x44, 0x01 ]
#currents_min = [ 0x5b, 0x00, 0x5b, 0x00, 0x5b, 0x00 ]
#currents_rand= [ 0xa2, 0x01, 0xa2, 0x01, 0xa2, 0x01 ]
led_min = 91	#minimum LED current as an integer
r_max = 736	#maximum red LED current as an integer
gb_max = 983	#maximum green and blue LED current as an integer

#configure gpio pin(s) as inputs or outputs
channel1 = 11
channel2 = 12
channel3 = 13
gpio.setup(channel1, gpio.OUT, initial=gpio.HIGH)	#output gpio for toggling projector
gpio.setup(channel2, gpio.IN)	#gpio input for measuring captivate gpio output
gpio.setup(channel3, gpio.IN)	#gpio input for measuring arduino gpio output

#add gpio event detector interrupt for captivate inputs
gpio.add_event_detect(channel2, gpio.RISING, read_captivate(bus,delay,captivate, mouse, keyboard), bouncetime=100)

#add gpio event detector interrupt for arduino inputs
gpio.add_even_detect(channel3, gpio.RISING, auto_shutdown(bus, delay, evm_sense, channel3), bouncetime=100)

#configure OPT3001 light sensors
bus = SMBus(busnum)
sensor_config(amb_sense)
sensor_config(evm_sense)
bus.close(busnum)

bus = SMBus(busnum)
while 1:
	try:
	
	
	
	except KeyboardInterrupt:
		bus.close()
		gpio.cleanup()
		#auto_shutdown(bus, delay, evm_sense, channel3)
	
	except Exception as ex:
		#get the type of error thrown and output it to terminal for debugging purposes
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format( type(ex).__name__, ex.args )
		print(message)
		
		#close i2c bus and gpio resources, then shutdown
		bus.close()
		gpio.cleanup()
		auto_shutdown(bus, delay, evm_sense, channel3)
