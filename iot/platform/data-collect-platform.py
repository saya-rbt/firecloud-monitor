# coding: utf-8
# Author: @sayabiws

## Libraries import
# Encryption
import nacl.utils
import nacl.secret
from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey, Box, PublicKey

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
# Keyfiles folder
keyfiles_f = "keys/"

# Communication variables
# ALL THOSE ARE HEX VALUES STORED IN STRINGS
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
	print ("Firecloud Monitor -- Data collect platform")
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

# def initKeyExchange(sk_data_collect, ser):
# 	pk_data_collect = sk_data_collect.public_key
# 	print("Waiting for key exchange...")
# 	input_ser = ser.read(54)
# 	# print(input_ser)
# 	# print(len(input_ser))
# 	print("Sensors public key received!")
# 	pk_sensors = input_ser[7:39]
# 	print(pk_sensors)
# 	flags = input_ser[:6].decode().split(";")
# 	# pk_sensors = a.split(";")[3].rstrip()
# 	print("Replying with our public key...")
# 	# print(pk_sensors)
# 	# print(len(pk_sensors))
# 	sent_pk = SENSORS_DEST_ADDR + message_types["THERE"] + pk_data_collect.encode()
# 	print(pk_data_collect)
# 	sent_pk_padded = pad(sent_pk)
# 	# print(sent_pk_padded)
# 	# print(len(sent_pk_padded))
# 	ser.write(sent_pk_padded)

# 	box = Box(sk_data_collect, nacl.public.PublicKey(pk_sensors))
# 	print("test:")
# 	print(box.encrypt(b"connard"))
# 	return box

	# print(pk_sensors.encode(Base64Encoder).decode())
	# print(unhex(SENSORS_DEST_ADDR))
	# print(unhex(message_types["HELLO"]))
	# print("-----")
	# print(bytes.fromhex(SENSORS_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder))
	# if (unhex(SENSORS_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode()) == (bytes.fromhex(SENSORS_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder)).decode():
	# 	print("yes")
	# else:
	# 	print("no")

def init_sbox(sensors_address):
	try:
		print("Opening keyfile for sensor " + sensors_address + "...")
		with open(keyfiles_f + sensors_address + ".keyfile", "rb") as keyfile:
			key = keyfile.readline()
		sbox = nacl.secret.SecretBox(key)
		return sbox
	except FileNotFoundError:
		print("No keyfile found for sensor " + sensors_address + "!")
		return None
		# with open(keyfiles_f + sensors_address.hex() + ".keyfile", "rb") as keyfile:
		# 	key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
		# 	keyfile.write(key)
	

## Main
if __name__ == "__main__":
	# sk_data_collect = PrivateKey.generate() # THIS MUST BE KEPT SECRET
	
	# print("Initiating key exchange...")
	initUART()

	connections = {}

	while True:
		print("Waiting for a message...")
		input_ser = ser.read(53)
		print("Received message!")
		print(input_ser)
		source_addr = bytes([input_ser[0]])
		# print(source_addr)
		source_cksm = bytes([input_ser[2]])
		# print(source_cksm)
		source_flag = bytes([input_ser[4]])
		# print(source_flag)
		source_data = input_ser[6:]
		# print(source_data)
		# print(message_types["HELLO"])
		# print(source_flag == message_types["HELLO"])

		# If someone tries to establish a connection, we check if we have a keyfile
		# for them.
		# If we don't, we send a NACK and refuse to handle the data.
		# If we do, we send a THERE and establish the connection.
		if source_flag == message_types["HELLO"]:
			print(source_addr.hex() + " is trying to (re)establish a connection.")
			sbox = init_sbox(source_addr.hex())
			if sbox is not None:
				connections[source_addr] = sbox
				print("Connection with " + source_addr.hex() + " established!")
				print("Sending THERE...")
				msg = source_addr + message_types["THERE"] + connections[source_addr].encrypt(b"THERE:0")
			else:
				print("Connection refused.")
				print("Sending NACK...")
				msg = source_addr + message_types["NACK"] + b"ERROR 01: no keyfile was found for this sensor."
		elif source_flag == message_types["DATA"]:
			print("Received data from " + source_addr.hex() + ".")
			if source_addr not in connections:
				print("No connection established with " + source_addr + "!")
				print("Sending NACK...")
				msg = source_addr + message_types["NACK"] + b"ERROR 02: Please establish a connection first!"
			else:
				print("Decrypting data...")
				source_data_dec = connections[source_addr].decrypt(source_data).decode('utf-8')
				print("Data is " + source_data_dec)
				print("Sending to the server... [TODO]")
				print("Sending ACK...")
				msg = source_addr + message_types["ACK"] + connections[source_addr].encrypt(b"ACK:SUC")
				print(msg)

		print(len(msg))
		ser.write(msg)
		print("Message sent!")
		msg = ""



	
	# data_collect_box = initKeyExchange(sk_data_collect, ser)

	# data = ""
	# while data != "stop":
	# 	print("Waiting for data to be sent...")
	# 	rcv_packet = ser.read(54)
	# 	print("Data received!")
	# 	# print(rcv_packet)
	# 	rcv_data = rcv_packet[7:]
	# 	print(rcv_data)
	# 	reception_error = False
	# 	try:
	# 		data = data_collect_box.decrypt(rcv_data)
	# 		print(data)
	# 	except nacl.exceptions.CryptoError:
	# 		print("Error while receiving data: CryptoError!")
	# 		reception_error = True
	# 	if rcv_data.find(b"ERROR") == 0:
	# 		print("Error with data checksum: did not verify!")
	# 		reception_error = True
	# 	if reception_error:
	# 		print("Preparing NACK...")
	# 		encnack = data_collect_box.encrypt(b"ER:NACK")
	# 		encmsg = SENSORS_DEST_ADDR + message_types["NACK"] + encnack
	# 		print("Sending NACK...")
	# 		print(encmsg)
	# 		ser.write(encmsg)
	# 		print("NACK sent!")
	# 	else:
	# 		print("Encrypting ACK...")
	# 		encack = data_collect_box.encrypt(b"MSG:ACK")
	# 		encmsg = SENSORS_DEST_ADDR + message_types["ACK"] + encack
	# 		print("Sending ACK...")
	# 		ser.write(encmsg)
	# 		print("ACK sent!")
	# if data == "stop":
	# 	closeUART()
	# 	print("Connection stopped by sensors.")

	# sensors_box = initKeyExchange(sk_sensors, ser)
	
	# TODO: replace with API yields when our API is set up
	# ack = ""
	# while(ack != "stop"):
	# 	print("Receiving data...")
	# 	encmessage = ser.readline().split(";")[3].rstrip()
	# 	decmessage = data_collect_box.decrypt(encmessage)
	# 	print(decmessage.decode("utf-8"))
	# 	ack = input("Response? ")
	# 	if ack != "stop":
	# 		ackmessg = SENSORS_DEST_ADDR + message_types["ACK"] + ack.encode()
	# 		print(ackmessg)
	# 		print(ackmessg.encode)
	# 		print("Sending " + ack + "...")
	# 		ser.write(ackmessg)
	# 		# We don't wait for a response, we just wait for another message
	# 	else:
	# 		closeUART()
	# 		print("Stopped.")