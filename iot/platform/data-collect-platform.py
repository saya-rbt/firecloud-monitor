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
SERIALPORT = "/dev/ttyUSB1"
# SERIALPORT = "/dev/tty.usbserial-DA00G4XZ"
BAUDRATE = 115200
ser = serial.Serial()

# Encryption variables


# Communication variables
# ALL THOSE ARE HEX VALUES STORED IN STRINGS
SENSORS_DEST_ADDR = "1E"
message_types = {"HELLO": "01", "THERE": "02", "DATA": "03", "ACK": "04", "NACK":"05"}

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
	print ("Firecloud Monitor -- Data collect platform")
	print("---\nStarting up serial monitor...")
	try:
		ser.open()
	except serial.SerialException:
		print("ERROR: Serial " + SERIALPORT + " port not available")
		exit()

def closeUART():
	ser.close()

def sendUARTMessage(msg):
	ser.write(msg.encode())

# Encryption functions
def unhex(hex):
	return bytes.fromhex(hex).decode("utf-8")

def initKeyExchange(sk_sensors, ser):
	pk_sensors = sk_sensors.public_key
	sendUARTMessage(unhex(SENSORS_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode())
	pk_data_collect = ser.read_until("\n\r")
	print(pk_data_collect)
	box = Box(sk_sensors, pk_data_collect)
	return box


	# print(pk_sensors.encode(Base64Encoder).decode())
	# print(unhex(SENSORS_DEST_ADDR))
	# print(unhex(message_types["HELLO"]))
	# print("-----")
	# print(bytes.fromhex(SENSORS_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder))
	# if (unhex(SENSORS_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode()) == (bytes.fromhex(SENSORS_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder)).decode():
	# 	print("yes")
	# else:
	# 	print("no")

## Main
if __name__ == "__main__":
	sk_data_collect = PrivateKey.generate() # THIS MUST BE KEPT SECRET
	
	# print("Initiating key exchange...")
	initUART()
	print("Waiting for key exchange...")
	pk_sensors = ser.read_until("\n\r").split(";")[3]
	print("Sensors public key received!")
	print(pk_sensors)
	data_collect_box(sk_data_collect, pk_sensors)

	# sensors_box = initKeyExchange(sk_sensors, ser)
	
	# TODO: replace with API yields when our API is set up
	ack = ""
	while(ack != "stop"):
		print("Receiving data...")
		encmessage = ser.read_until("\n\r").split(";")[3]
		decmessage = data_collect_box.decrypt(encmessage)
		print(decmessage)
		ack = input("Response? ")
		ackmessg = unhex(SENSORS_DEST_ADDR) + unhex(message_types["ACK"]) + ack
		print(ackmessg)
		print(ackmessg.encode)
		if ack != "stop":
			print("Sending " + ack + "...")
			sendUARTMessage(ack)
			# We don't wait for a response, we just wait for another message
		else:
			closeUART()
			print("Stopped.")