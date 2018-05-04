#!/usr/bin/python

from pykeyboard import PyKeyboard

k = PyKeyboard()

k.press_key(k.shift_key)
k.press_key(k.alt_key)
k.tap_key('t')
k.release_key(k.shift_key)
k.release_key(k.alt_key)
