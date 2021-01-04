'''
This file will be used to process the packets that are received from the ground. Before the packets reach this file, they will be sent to the radio and then over UART to the pi.
The pythonInterrupt.py file monitors the UART buffer, and when data is received it will gather the data byte by byte and then parse the data for the header and footer that should be located on either end of our packets.
The header and footer is the Hex representation of 'GASPACS'. The pythonInterrupt.py takes the packet data located in between the header and footer and then calls the processPacket() method located in this file, passing in an argument containing the packet data.
processPacket() will convert the packet data to binary, and then go through bit by bit and perform the functionality specified in the packet.
'''
# NOTE: This code is not asyncronous currently.
import sys
sys.path.append('../')
import time
import os.path
from os import system
from Drivers.camera import Camera
import Drivers.boomDeployer as boomDeployer
import smbus
import hmac

def processAX25(AX25):  #Placeholder function
	#Check AX25 Transmission flag, if it is OK then open a pyserial connection and transmit the content of the packet
	pass

async def processPacket(packetData):
	print('Processing packet')
	# Packet data comes in as hex, need to convet to binary to parse
	binaryDataLength = len(packetData) * 4
	print('bin data len' + str(binaryDataLength))
	binaryData = format(int(packetData,16), 'b').zfill(binaryDataLength)
	secretKey = b'SECRETKEY'

	if binaryData[0:8] == '00000000':
		# This is a TX Schedule packet.
		print("TX Schedule Packet")

		# Get window start delta T
		windowStartBinary = binaryData[8:40]
		windowStartDecimal = int(windowStartBinary,2)
		print("Window start in seconds: ", windowStartDecimal)

		# Get window duration
		windowDurationBinary = binaryData[40:56]
		windowDurationDecimal = int(windowDurationBinary,2)
		print("Window duration in seconds: ", windowDurationDecimal)

		# Get data type
		dataTypeBinary = binaryData[56:64]
		dataTypeDecimal = int(dataTypeBinary,2)
		print("Data type: ", dataTypeDecimal)

		# Get picture number
		pictureNumberBinary = binaryData[64:80]
		pictureNumberDecimal = int(pictureNumberBinary,2)
		print("Picture number: ", pictureNumberDecimal)

		# Get "Start From Beginning"
		startFromBeginning = binaryData[80:88]
		print("Start from beginning: ", startFromBeginning)

		# Get the appended hash - it is a 16 byte (128 bit) value
		receivedHash = binaryData[88:]
		print("Received Hash: ", receivedHash)

		# Generated hash from received data
		generatedHash = hmac.new(secretKey, bytes(binaryData[0:88], 'utf-8'))
		generatedHashHex = generatedHash.hexdigest()
		generatedHashLength = len(generatedHashHex) * 4
		generatedHashBinary = format(int(generatedHashHex,16), 'b').zfill(generatedHashLength)
		print("Generated hash: ", generatedHashBinary)
		if receivedHash == generatedHashBinary:
			print("Hashes match! Writing window")
			writeTXWindow(windowStartDecimal, windowDurationDecimal, dataTypeDecimal, pictureNumberDecimal, startFromBeginning)

		else:
			print("Hashes do not match, will not save window!")

	else:
		# This is a command packet
		print("Command packet")

		# Validate HMAC Hash
		# Note, hash is 16 bytes (128 bits). Command packet is 1 byte (8 bits)
		receivedHash = binaryData[56:185]
		print("Received Hash: ", receivedHash)

		# Generated hash from received data
		generatedHash = hmac.new(secretKey, bytes(binaryData[0:56], 'utf-8'))
		generatedHashHex = generatedHash.hexdigest()
		generatedHashLength = len(generatedHashHex) * 4
		generatedHashBinary = format(int(generatedHashHex,16), 'b').zfill(generatedHashLength)
		print("Generated hash: ", generatedHashBinary)
		if receivedHash == generatedHashBinary:
			print("Hashes match! Executing commands")

			if binaryData[8:16] == '00000000':
				# Turn off Transmitter
				print("Turn off Transmissions")
				disableTransmissions()
			else:
				#Turn on Transmitter
				print("Turn on Transmitter")
				enableTransmissions()

			if binaryData[16:24] == '00000000':
				# DO NOT Clear TX Schedule and Progress
				print("Do NOT Clear TX Schedule and Progress")
			else:
				# Clear TX Schedule & Progress
				print("Clear TX Schedule and Progress")
				clearTXFile()
				clearTXProgress()

			if binaryData[24:32] == '00000000':
				# Do not take picture
				print("Do not take picture")
			else:
				# Take picture
				print("Take picture")
				cam = Camera()
				cam.takePicture()

			if binaryData[32:40] == '00000000':
				# Do not deploy boom
				print("Do not deploy boom")
			else:
				# Deploy boom
				print("Deploy boom")
				deployer = boomDeployer.BoomDeployer()
				await deployer.deploy()

			if binaryData[40:48] == '00000000':
				# Do not reboot
				print("Do not reboot")
			else:
				#Send reboot command to Beetle
				print("Reboot")
				bus = smbus.SMBus(1)
				address = 0x08
				bus.write_byte(address, 1)

			if binaryData[48:56] == '00000000':
				# Turn off AX25
				print("Turn off AX25")
				disableAX25()
			else:
				#Turn on AX25
				print("Turn on AX25")
				enableAX25()
		else:
			print("Hashes do not match, will not execute commands!")


def writeTXWindow(windowStart, windowDuration, dataType, pictureNumber, startFromBeginning):
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will write the TX window packet information to a file. Pass in the window start (delta T), window duration, data type, picture number, and Start From Beginning (1/0).
	# Note that this function saves the window start as an actual time, not a delta T - this is critical.

	# Convert window start from delta T to seconds since epoch
	windowStartTime = windowStart + int(time.time())
	print("Current time: ", int(time.time()))
	print("Start time: ", windowStartTime)
	
	TXWindow_File = open("/home/pi/Integration/CubeWorks/TXISR/data/txWindows.txt", "a+")
       
	#write the data to the file,
	TXWindow_File.write(str(windowStartTime)+',')
	TXWindow_File.write(str(windowDuration)+',')
	TXWindow_File.write(str(dataType)+',')
	TXWindow_File.write(str(pictureNumber)+',')
	TXWindow_File.write(str(startFromBeginning))
	TXWindow_File.write('\n')
	
	# close file
	TXWindow_File.close()
	
def disableTransmissions():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
	transmissionFlag_File = open("/home/pi/Integration/CubeWorks/TXISR/data/transmissionFlag.txt", "w")
	
	# write the data to the file,
	transmissionFlag_File.write("Disabled")
	
	# close the file
	transmissionFlag_File.close()
	
def enableTransmissions():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
	transmissionFlag_File = open("/home/pi/Integration/CubeWorks/TXISR/data/transmissionFlag.txt", "w")
	
	# write the data to the file,
	transmissionFlag_File.write("Enabled")
	
	# close file
	transmissionFlag_File.close()
	
def disableAX25():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
	AX25Flag_File = open("/home/pi/Integration/CubeWorks/TXISR/data/AX25Flag.txt", "w")
	
	# write the data to the file,
	AX25Flag_File.write("Disabled")
	
	# close the file
	AX25Flag_File.close()
	
def enableAX25():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will set a flag that will disable the radio transmissions. We will check the flag before making any transmissions.
	AX25Flag_File = open("/home/pi/Comms/CubeWorks/TXISR/data/AX25Flag.txt", "w")
	
	# write the data to the file,
	AX25Flag_File.write("Enabled")
	
	# close file
	AX25Flag_File.close()
	
def clearTXFile():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function clears the TX windows file
	transmissionFlag_File = open("/home/pi/Integration/CubeWorks/TXISR/data/txWindows.txt", "w")
	
	# close file
	transmissionFlag_File.close()
	
def clearTXProgress():
	#check all files to see if they are working
	fileChecker.fullReset()
	# This function will clear the file that saves which timestamp has been transmitted most recently for each data type
	print("I don't know which file to clear!!!")
	progressFile = open("/home/pi/Integration/CubeWorks/TXISR/data/flagsFile.txt", "w")
	progressFile.write('0\n')
	progressFile.write('0\n')
	progressFile.write('0\n')
	progressFile.write('0\n')
	progressFile.write('0\n')

# Command packet
# processPacket('C8')
# TX Window Packet
#processPacket('0000000F007801000000')
