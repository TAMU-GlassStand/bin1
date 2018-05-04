#!/bin/sh

/usr/bin/chromium-browser --enable-logging --v=1 --user-data-dir=/home/pi/bin/chrome-debug /home/pi/Desktop/html/TI_Glass_Stand_home.html &
/bin/sleep 7s
/usr/bin/xdotool search --name "TI_Glass_Stand_home.html" windowfocus key F11
#python /home/pi/Desktop/html/ti_glass_stand.py &



#while [ "$(ps -u pi | grep chromium)" != "" ]; do
#	continue
#done

#pkill python