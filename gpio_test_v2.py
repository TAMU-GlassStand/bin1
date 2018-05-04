#!/usr/bin/python

import RPi.GPIO as gpio
import time

gpio.cleanup()

#setup gpio pins to be defined based on their pin number on the gpio header
gpio.setmode(gpio.BOARD)

channel=11
gpio.setup(channel, gpio.OUT, initial=gpio.HIGH)

start = time.time()
threshold = 2
limit = 2.5
while time.time()<start+3:
	if time.time()>=start+threshold and time.time()<start+limit and gpio.input(channel)==1:
		gpio.output(channel, gpio.LOW)
	elif time.time()>=start+limit and gpio.input(channel)==0:
		gpio.output(channel, gpio.HIGH)
	#print( gpio.input(channel) )
	time.sleep(0.01)

gpio.cleanup()