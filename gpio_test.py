#!/usr/bin/python

import RPi.GPIO as gpio
import time

#setup gpio pins to be defined based on their pin number on the gpio header
gpio.setmode(gpio.BOARD)

channel=12
gpio.setup(channel, gpio.IN, pull_up_down = gpio.PUD_UP)

start = time.time()
try:
	while True:
		pin_value = gpio.input(channel)
		print(pin_value)
		time.sleep(0.1)
except KeyboardInterrupt:
	gpio.cleanup()