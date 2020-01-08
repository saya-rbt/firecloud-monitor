# coding: utf-8
# Author: @sayabiws

## Libraries import
# Encryption
import nacl.utils
from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey, Box

# Serial
import serial

# Other
import binascii

## Variables
# Microcontroller variables

# IMPORTANT: that means you have to plug the 
# sensors microcontroller first!
SERIALPORT = "/dev/ttyUSB0"
# SERIALPORT = "/dev/tty.usbserial-DA00G4XZ"
BAUDRATE = 115200
ser = serial.Serial()

# Encryption variables


# Communication variables
# ALL THOSE ARE HEX VALUES STORED IN STRINGS
DATA_COLLECT_DEST_ADDR = b"\x1e"
message_types = {"HELLO": b"\x01", "THERE": b"\x02", "DATA": b"\x03", "ACK": b"\x04", "NACK":b"\x05"}

## Actual code

# Serial functions
def initUART():  
	# ser = serial.Serial(SERIALPORT, BAUDRATE)
	ser.port=SERIALPORT
	ser.baudrate=BAUDRATE
	ser.bytesize = serial.EIGHTBITS #number of bits per bytes
	ser.parity = serial.PARITY_NONE #set parity check: no parity
	ser.stopbits = serial.STOPBITS_ONE #number of stop bits
	ser.timeout = None		  #block read

	# ser.timeout = 0			 #non-block read
	# ser.timeout = 2			  #timeout block read
	ser.xonxoff = False	 #disable software flow control
	ser.rtscts = False	 #disable hardware (RTS/CTS) flow control
	ser.dsrdtr = False	   #disable hardware (DSR/DTR) flow control
	#ser.writeTimeout = 0	 #timeout for write
	print ("Firecloud Monitor -- Test platform")
	print("---\nStarting up serial monitor...")
	try:
		ser.open()
	except serial.SerialException:
		print("ERROR: Serial " + SERIALPORT + " port not available")
		exit()

def closeUART():
	ser.close()

def byteify(hexstr):
	return bytes.fromhex(hexstr)

def unhex(hex):
	return bytes.fromhex(hex).decode("utf-8")

def keyEcho(sk_sensors, ser):
	pk_sensors = sk_sensors.public_key
	
	print("Sending a public key...")
	# print(DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode(Base64Encoder))
	
	# msg_to_echo = byteify(DATA_COLLECT_DEST_ADDR) + byteify(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder) + "\n\r".encode()
	msg_to_echo = DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode(Base64Encoder) + "\n".encode()
	
	print(msg_to_echo)
	print(len(msg_to_echo))
	
	ser.write(msg_to_echo)
	print("Waiting for the microcontroller echo...")
	echo = ser.readline() # TODO: handle flags
	
	print("Echo received!")
	print(echo)
	print(msg_to_echo == echo)
	# box = Box(sk_sensors, echo)
	# return box

## Main
if __name__ == "__main__":
	sk_sensors = PrivateKey.generate() # THIS MUST BE KEPT SECRET
	
	initUART()
	print("Initiating key echo...")
	keyEcho(sk_sensors, ser)
	
	# TODO: replace with API yields when our API is set up
	# msg = ""
	# while(msg != "stop"):
	# 	msg = input("Message? ")
	# 	if msg != "stop":
	# 		print("Encrypting " + msg + "...")
	# 		encrypted = sensors_box.encrypt(msg)
	# 		print("Sending " + msg + "...")
	# 		sendUARTMessage(encrypted + "\n\r")

	# 		# Wait for ACK
	# 		encresponse = unhex(ser.read_until("\n\r")).split(";")[3].rstrip()
	# 		decresponse = sensors_box.decrypt(encresponse)

	# 		print(decresponse.decode(utf-8))
	# 	else:
	# 		closeUART()
	# 		print("Stopped.")