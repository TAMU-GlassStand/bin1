import RPi.GPIO as GPIO
import time

while True:
	# read all text in file then close file
	# should help avoid problem of file being written by UI
	# while file text is being analyzed
	file = open('/home/pi/bin/chrome-debug/chrome_debug.log','r')
	text = file.readlines()
	file.close()
	
	brightness = 0
	# create search string variable(s) to find desired data from file
	search_str1 = 'brightness: '
	for line in text:
		if search_str1 in line:
			start = line.find(search_str1)
			shift = len(search_str1)
			end = line.find('"',start)
			brightness = line[start+shift:end]
			##print(line)
	# print(brightness)
	# print('end of loop\n')
	
	output = open('/home/pi/bin/brightness_setting.txt','w')
	output.write(brightness)
	# output.write('end of loop\n')
	output.close()
	time.sleep(10)

