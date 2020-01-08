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
	print ("Firecloud Monitor -- Sensors platform")
	print("---\nStarting up serial monitor...")
	try:
		ser.open()
	except serial.SerialException:
		print("ERROR: Serial " + SERIALPORT + " port not available")
		exit()

def closeUART():
	ser.close()

# Encryption functions
def unhex(hex):
	return bytes.fromhex(hex).decode("utf-8")

def pad(msg):
	if len(msg) < 49:
		for i in range(49-len(msg)):
			msg += b"\xff"
	return msg

def initKeyExchange(sk_sensors, ser):
	pk_sensors = sk_sensors.public_key
	
	print("Sending our public key...")
	# print(DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode(Base64Encoder).decode())
	
	sent_pk = DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode()
	
	print(pk_sensors)
	# print(len(sent_pk))
	sent_pk_padded = pad(sent_pk)
	# print(sent_pk_padded)
	# print(len(sent_pk_padded))
	
	ser.write(sent_pk_padded)
	
	print("Waiting for the data collect platform...")
	input_ser = ser.read(54)
	pk_data_collect = input_ser[8:40]
	# pk_data_collect = ser.readline().decode()#.split(";")[3].rstrip() # TODO: handle flags
	print("Data collect public key received!")
	print(pk_data_collect)
	# flags = input_ser[:6].decode().split(";")
	
	box = Box(sk_sensors, nacl.public.PublicKey(pk_data_collect))
	print("test:")
	print(box.encrypt(b"connard"))
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
		print("Encrypting " + fire + "...")
		encrypted = sensors_box.encrypt(fire.encode())
		encmsg = DATA_COLLECT_DEST_ADDR + message_types["DATA"] + encrypted
		print("Sending " + fire + "...")
		print(encmsg)
		ser.write(encmsg)
		print("Sent!")
		# Wait for ACK
		print("Waiting for ACK...")
		encresponse = ser.read(54)
		print(encresponse)
		while encresponse[5] == message_types["NACK"]:
			print("NACK received. Resending " + fire + "...")
			ser.write(encmsg)
			print("Resent!")
			print("Waiting again for ACK...")
			encresponse = ser.read(54)
		encresponse_data = encresponse[7:]
		try:
			decresponse = sensors_box.decrypt(encresponse_data)
			print("ACK received:")
			print(decresponse.decode("utf-8"))
		except nacl.exceptions.CryptoError:
			print("Error when decrypting!")
	if fire == "stop":
		closeUART()
		print("Stopped.")