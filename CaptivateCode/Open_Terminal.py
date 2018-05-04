#!/usr/bin/python


from pymouse import PyMouse
from pykeyboard import PyKeyboard

m=PyMouse()
k=PyKeyboard()

#k.press_keys(['ctrl_key','alt_key','t'])

k.press_key(k.control_key)
k.press_key(k.alt_key)
k.tap_key('t')
k.release_key(k.control_key)
k.release_key(k.alt_key)

