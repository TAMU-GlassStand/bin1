#!/usr/bin/python

from pykeyboard import PyKeyboard
import time

k = PyKeyboard()
time.sleep(3)
k.press_key(k.alt_key)
k.tap_key(k.function_keys[4])
k.release_key(k.alt_key)
