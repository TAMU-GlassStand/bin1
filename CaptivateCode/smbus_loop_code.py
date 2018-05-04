while 1:
	
	bus.write_i2c_block_data(0x0a, 0x00, data0) #Write which sensor element looking for (buttons)
	read=bus.read_i2c_block_data(address, 0, 6)
	read1=read[0] #Byte 1
	read2=read[1] #Byte 2
	read3=read[2] #Byte 3 (Changes based on button being pressed)
	read4=read[3] #Byte 4
	read5=read[4] #Byte 5
	read6=read[5] #Byte 6 (Changes when touch/proximity is detected)

	touchbit=read6 & 0x01

	if touchbit==1 and read3!=prev:
		prev=read3
		touchbit=-1

		if read3==0:
			print"Button 1 was pressed: Start"

			# Start/Restart
			close_window
			time.sleep(1)
			start_UI

		elif read3==5:
			print"Button 6 was pressed: Setting"
			
			#Settings
			settings_page		

		elif read3==9:
			print"Button 10 was pressed: Google Drive"
			
			#Google Drive
			google_page

		elif read3==13:
			print"Button 14 was pressed: Removable Storage"
			
			#Removable Storage
			removable_page

		elif read3==2:
			print"Button 3 was pressed: Brightness Increase"

			#Brightness Increase
			bright_up
				
		elif read3==12:
			print"Button 13 was pressed: Brightness Decrease"

			#Brightness Decrease
			bright_down
	
		elif read3==8:
			print"Button 9 was pressed: Up"

			#Up
			tab_back

		elif read3==11:
			print"Button 12 was pressed: Down"

			#Down
			tab_forward

		elif read3==4:
			print"Button 5 was pressed: Back"

			#Back
			page_back

		if read3==7:
			print"Button 8 was pressed: Enter"

			#Enter
			enter_button

		if read3==1:
			print"Button 2 was pressed: Home Page"

			# Home Page
			
		if read3==14:
			print"Button 15 was pressed: Zoom In"

			# Zoom In
			# NOT WORKING ON EIC BOARD
			zoom_in

		if read3==15:
			print"Button 16 was pressed: Zoom Out"

			# Zoom Out
			# NOT WORKING ON EIC BOARD
			zoom_out

		if read3==6:
			print"Button 7 was pressed: Previous Page"

			#Previous Page
			prev_page		

		if read3==3:
			print"Button 4 was pressed: Next Page"

			#Next Page
			next_page

		if read3==10:
			print"Button 11 was pressed: Fit to Page"

			# Fit to Page
			# Zoom is currently not working
			fit_page

	if read6==0:
		touch=-1
		prev=-1
		read3=-1
