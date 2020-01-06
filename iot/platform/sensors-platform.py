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
DATA_COLLECT_DEST_ADDR = "1E"
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
	print ("Firecloud Monitor -- Sensors platform")
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
	print("Sending our public key...")
	sent_pk = unhex(DATA_COLLECT_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode() + "\n\r"
	print(sent_pk)
	print(len(sent_pk.encode()))
	sendUARTMessage(sent_pk)
	print("Waiting for the data collect platform...")
	pk_data_collect = unhex(ser.read_until("\n\r")).split(";")[3].rstrip() # TODO: handle flags
	print("Data collect public key received!")
	print(pk_data_collect)
	box = Box(sk_sensors, pk_data_collect)
	return box


	# print(pk_sensors.encode(Base64Encoder).decode())
	# print(unhex(DATA_COLLECT_DEST_ADDR))
	# print(unhex(message_types["HELLO"]))
	# print("-----")
	# print(bytes.fromhex(DATA_COLLECT_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder))
	# if (unhex(DATA_COLLECT_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode()) == (bytes.fromhex(DATA_COLLECT_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder)).decode():
	# 	print("yes")
	# else:
	# 	print("no")

## Main
if __name__ == "__main__":
	sk_sensors = PrivateKey.generate() # THIS MUST BE KEPT SECRET
	
	initUART()
	print("Initiating key exchange...")
	sensors_box = initKeyExchange(sk_sensors, ser)
	
	# TODO: replace with API yields when our API is set up
	fire = ""
	while(fire != "stop"):
		fire = input("Message? ")
		if fire != "stop":
			print("Encrypting " + fire + "...")
			encrypted = sensors_box.encrypt(fire)
			print("Sending " + fire + "...")
			sendUARTMessage(encrypted + "\n\r")

			# Wait for ACK
			encresponse = unhex(ser.read_until("\n\r")).split(";")[3].rstrip()
			decresponse = sensors_box.decrypt(encresponse)

			print(decresponse.decode(utf-8))
		else:
			closeUART()
			print("Stopped.")