# coding: utf-8
# Author: @sayabiws

## Libraries import
# Encryption
import nacl.utils
import nacl.secret
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
# Keyfiles folder
keyfiles_f = "keys/"

# Communication variables
# ALL THOSE ARE HEX VALUES STORED IN STRINGS
DATA_COLLECT_DEST_ADDR = b"\x1e"
SENSORS_ADDRESS = b"\x05"
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

# def initKeyExchange(sk_sensors, ser):
# 	pk_sensors = sk_sensors.public_key
	
# 	print("Sending our public key...")
# 	# print(DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode(Base64Encoder).decode())
	
# 	sent_pk = DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + pk_sensors.encode()
	
# 	print(pk_sensors)
# 	# print(len(sent_pk))
# 	sent_pk_padded = pad(sent_pk)
# 	# print(sent_pk_padded)
# 	# print(len(sent_pk_padded))
	
# 	ser.write(sent_pk_padded)
	
# 	print("Waiting for the data collect platform...")
# 	input_ser = ser.read(54)
# 	pk_data_collect = input_ser[8:40]
# 	# pk_data_collect = ser.readline().decode()#.split(";")[3].rstrip() # TODO: handle flags
# 	print("Data collect public key received!")
# 	print(pk_data_collect)
# 	# flags = input_ser[:6].decode().split(";")
	
# 	box = Box(sk_sensors, nacl.public.PublicKey(pk_data_collect))
# 	print("test:")
# 	print(box.encrypt(b"connard"))
# 	return box


	# print(pk_sensors.encode(Base64Encoder).decode())
	# print(unhex(DATA_COLLECT_DEST_ADDR))
	# print(unhex(message_types["HELLO"]))
	# print("-----")
	# print(bytes.fromhex(DATA_COLLECT_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder))
	# if (unhex(DATA_COLLECT_DEST_ADDR) + unhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder).decode()) == (bytes.fromhex(DATA_COLLECT_DEST_ADDR) + bytes.fromhex(message_types["HELLO"]) + pk_sensors.encode(Base64Encoder)).decode():
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

def init_connection(data_collect_address, ser):
	print("Establishing connection with " + DATA_COLLECT_DEST_ADDR.hex())
	msg = DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + b"HELLO: " + SENSORS_ADDRESS + b" is trying to establish a connection..."
	established = False
	while not established:
		print("Sending HELLO...")
		print(msg)
		ser.write(msg)
		print("HELLO sent!")
		print("Waiting for THERE...")
		ans = ser.read(53)
		print(ans)
		print(len(ans))
		source_addr = bytes([ans[0]])
		source_cksm = bytes([ans[2]])
		source_flag = bytes([ans[4]])
		source_data = ans[6:]
		if source_flag == message_types["THERE"]:
			print("Connection established!")
			established = True
		elif source_flag == message_types["NACK"]:
			if source_data.find(b"ERROR 01") != -1:
				return False
			else:
				continue
	return True

## Main
if __name__ == "__main__":
	# Initiating the UART
	initUART()

	# Initiating connection with the data collect platform
	if not init_connection(DATA_COLLECT_DEST_ADDR, ser):
		print("Could not establish collection: no keyfile!")
	else:
		sbox = init_sbox(SENSORS_ADDRESS.hex())
		if sbox is not None:
			data = ""
			while data != "stop":
				data = input("Message? ")
				
				print("Encrypting " + data + "...")
				encrypted = sbox.encrypt(data.encode())
				encmsg = DATA_COLLECT_DEST_ADDR + message_types["DATA"] + encrypted
				
				print("Sending " + data + "...")
				print(encmsg)
				print(len(encmsg))
				ser.write(encmsg)
				print("Sent!")

				print("Waiting for a response...")
				ans = ser.read(53)
				print(ans)
				source_addr = bytes([ans[0]])
				source_cksm = bytes([ans[2]])
				source_flag = bytes([ans[4]])
				source_data = ans[6:]
				while source_flag == message_types["NACK"]:
					print("NACK received. Resending " + fire + "...")
					ser.write(encmsg)
					print("Resent!")
					print("Waiting again for ACK...")
					encresponse = ser.read(53)
				# encresponse_data = source_data
				if source_flag == message_types["ACK"]:
					print("ACK received!")
				else:
					print("ERROR: wrong response!")
				# try:
				# 	decresponse = sbox.decrypt(encresponse_data)
				# 	print("ACK received:")
				# 	print(decresponse.decode("utf-8"))
				# except nacl.exceptions.CryptoError:
				# 	print("Error when decrypting!")
				data = ""
		else:
			print("Stopped: couldn't establish a SecretBox.")


	# sk_sensors = PrivateKey.generate() # THIS MUST BE KEPT SECRET
	
	# initUART()
	# print("Initiating key exchange...")
	# sensors_box = initKeyExchange(sk_sensors, ser)
	
	# # TODO: replace with API yields when our API is set up
	# fire = ""
	# while(fire != "stop"):
	# 	fire = input("Message? ")
	# 	print("Encrypting " + fire + "...")
	# 	encrypted = sensors_box.encrypt(fire.encode())
	# 	encmsg = DATA_COLLECT_DEST_ADDR + message_types["DATA"] + encrypted
	# 	print("Sending " + fire + "...")
	# 	print(encmsg)
	# 	ser.write(encmsg)
	# 	print("Sent!")
	# 	# Wait for ACK
	# 	print("Waiting for ACK...")
	# 	encresponse = ser.read(54)
	# 	print(encresponse)
	# 	while encresponse[5] == message_types["NACK"]:
	# 		print("NACK received. Resending " + fire + "...")
	# 		ser.write(encmsg)
	# 		print("Resent!")
	# 		print("Waiting again for ACK...")
	# 		encresponse = ser.read(54)
	# 	encresponse_data = encresponse[7:]
	# 	try:
	# 		decresponse = sensors_box.decrypt(encresponse_data)
	# 		print("ACK received:")
	# 		print(decresponse.decode("utf-8"))
	# 	except nacl.exceptions.CryptoError:
	# 		print("Error when decrypting!")
	# if fire == "stop":
	# 	closeUART()
	# 	print("Stopped.")