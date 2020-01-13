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
import datetime
import time

# Servers
import requests

## Variables
# Microcontroller variables

# IMPORTANT: that means you have to plug the 
# sensors microcontroller first!
SERIALPORT = "/dev/ttyUSB0"
# SERIALPORT = "/dev/tty.usbserial-DA00G4XZ"
BAUDRATE = 115200
ser = serial.Serial()

# Servers variables
serv_address = "http://192.168.0.10"
serv_port = 8000

# Timezone offset
tz_offset = 1

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
	ser.timeout = 5			  #timeout block read
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

# init_sbox: will return an NaCl SecretBox initialized
# by the key found in the keyfile provided.
# Takes a bytes.hex() (ie. a 2 character hexadecimal string)
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

# init_connection: will return True or False depending on whether
# the data collect platform (the server) could find our key in its database
# and send a THERE message or not
# Takes a byte with the platform address and the serial port to send data through
def init_connection(data_collect_address, ser):

	print("Establishing connection with " + DATA_COLLECT_DEST_ADDR.hex())

	# Crafting our packet
	msg = DATA_COLLECT_DEST_ADDR + message_types["HELLO"] + b"HELLO: " + SENSORS_ADDRESS + b" is trying to establish a connection..."
	established = False

	# We retry to establish a connection until we have either a THERE or a NACK
	while not established:
		print("Sending HELLO...")
		ser.write(msg)
		print("HELLO sent!")
		print("Waiting for THERE...")
		ans = ser.read(53)
		if len(ans) != 53:
			print(len(ans))
			print("ERROR: response timeout. Resending...")
			continue
		else:
			source_addr = bytes([ans[0]])
			source_cksm = bytes([ans[2]])
			source_flag = bytes([ans[4]])
			source_data = ans[6:]

			# Those are the two responses we expect.
			# If we get anything else, we retry.
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

	last_checked = datetime.datetime.now()

	# Initiating connection with the data collect platform
	if not init_connection(DATA_COLLECT_DEST_ADDR, ser):
		print("Could not establish collection: no keyfile!")
	else:
		# Instantiating the SecretBox only when the connection is established
		sbox = init_sbox(SENSORS_ADDRESS.hex())
		if sbox is not None:
			data = ""
			# We use this for tests before hooking it to the API
			sending = False
			while data != "stop it":
				to_send = []
				if not sending:
					# print("TODO: Get the data from the API instead")
					print("Getting data from the API...")
					fires_request = requests.get(serv_address + ":" + str(serv_port) + "/fires")
					# print(fires_request)
					fires = fires_request.json()
					# print(fires)
					# print(fires)
					if not fires:
						print("No data. Continuing.")
					for fire in fires:
						fire_update_date = datetime.datetime.strptime(fire["updated"],"%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours = tz_offset)
						if fire_update_date > last_checked:
							sensor_request = requests.get(fire["sensor"])
							sensor = sensor_request.json()
							data = "(" + str(sensor["posx"]) + "," + str(sensor["posy"]) + "," + str(fire["intensity"]) + ")"
							to_send.append(data)
							sending = True
						else:
							continue
					if not to_send:
						print("No new data. Continuing.")
					last_checked = datetime.datetime.now()
				
				if sending:
					for data in to_send:
						# Encrypting the message
						print("Encrypting " + data + "...")
						encrypted = sbox.encrypt(data.encode())
						encmsg = DATA_COLLECT_DEST_ADDR + message_types["DATA"] + encrypted
						
						# Sending the message through the UART
						print("Sending " + data + "...")
						ser.write(encmsg)
						print("Sent!")

						# Waiting for a response from the data collect platform
						print("Waiting for a response...")
						ans = ser.read(53)
						if len(ans) != 53:
							print("ERROR: response timeout! Skipping.")
							sending = False
							continue
						else:
							source_addr = bytes([ans[0]])
							source_cksm = bytes([ans[2]])
							source_flag = bytes([ans[4]])
							source_data = ans[6:]

							# If we receive a NACK, we resend the message until we get an
							# ACK response
							while source_flag == message_types["NACK"]:
								print("NACK received. Resending " + data + "...")
								ser.write(encmsg)
								print("Resent!")
								print("Waiting again for ACK...")
								encresponse = ser.read(53)
								if len(encresponse) != 53:
									print("ERROR : response timeout!")
									sending = True
									continue

							# If we get an ACK, it's all good
							if source_flag == message_types["ACK"]:
								print("ACK received!")
								sending = False
								continue
							# Any other response will print an error
							else:
								print("ERROR: wrong response!")
								sending = False
								continue
				time.sleep(5)
		# If the connection fails, we stop.
		else:
			print("Stopped: couldn't establish a SecretBox.")