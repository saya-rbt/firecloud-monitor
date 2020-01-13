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
import json

# Servers
import requests
import paho.mqtt.client as mqttclient

## Variables
# Microcontroller variables

# IMPORTANT: that means you have to plug the 
# sensors microcontroller first!
SERIALPORT = "/dev/ttyUSB1"
# SERIALPORT = "/dev/tty.usbserial-DA00G4XZ"
BAUDRATE = 115200
ser = serial.Serial()

# Timezone offset
tz_offset = 1

# Servers variables
serv_address = "http://192.168.0.10"
serv_port = 8001

# Encryption variables
# Keyfiles folder
keyfiles_f = "keys/"

# Communication variables
# ALL THOSE ARE HEX VALUES STORED IN STRINGS
message_types = {"HELLO": b"\x01", "THERE": b"\x02", "DATA": b"\x03", "ACK": b"\x04", "NACK":b"\x05"}

# Server variables
with open("mqtt.cfg") as mqttfile:
	cfg = mqttfile.readlines()
	mqtt_broker = cfg[0].rstrip()
	mqtt_port = int(cfg[1].rstrip())


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
	# ser.timeout = 5			  #timeout block read
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

# Backend functions
def mqtt_on_publish(client, data, result):
	print("Data published on MQTT!")
	pass

## Main
if __name__ == "__main__":
	# Initiating the UART
	initUART()

	# The data collect platform can store connections from several sensor ones
	# This dict will have the address of the platform as key and the 
	# corresponding NaCl SecretBox as a value
	connections = {}

	mqtt_client = mqttclient.Client("data_collect")
	mqtt_client.on_publish = mqtt_on_publish
	mqtt_client.connect(mqtt_broker, mqtt_port)

	while True:
		# Listening for a message
		print("Waiting for a message...")
		input_ser = ser.read(53)
		print("Received message!")
		source_addr = bytes([input_ser[0]])
		source_cksm = bytes([input_ser[2]])
		source_flag = bytes([input_ser[4]])
		source_data = input_ser[6:]

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
		
		# Here we handle the DATA messages
		elif source_flag == message_types["DATA"]:
			print("Received data from " + source_addr.hex() + ".")
			if source_addr not in connections:
				print("No connection established with " + source_addr + "!")
				print("Sending NACK...")
				msg = source_addr + message_types["NACK"] + b"ERROR 02: Please establish a connection first!"
			else:
				print("Decrypting data...")
				try:
					source_data_dec = connections[source_addr].decrypt(source_data).decode('utf-8')
					print("Data is " + source_data_dec)
					data_split = source_data_dec.strip("()").split(",")
					print("Sending to the server... [TODO]")

					print("Getting the fire we need...")
					sensors_req = requests.get(serv_address + ":" + str(serv_port) + "/sensors/")
					sensors = sensors_req.json()
					# print(sensors)
					# for sensor in sensors:
					# 	print(sensor)
					# 	print(sensor["posx"])
					# 	print(sensor["posy"])
					# 	# print(data_split[0] == sensor["posx"])
					# 	if sensor["posx"] == int(data_split[0]) and sensor["posy"] == int(data_split[1]):
					# 		print(sensor["id"])
					sensor_id = [sensor["id"] for sensor in sensors if sensor["posx"] == int(data_split[0]) and sensor["posy"] == int(data_split[1])][0]
					# print(sensor_id)
					sensor = [sensor for sensor in sensors if sensor["id"] == sensor_id][0]
					fire = sensor["fires"]
					if not fire:
						fire = {"latitude": sensor["latitude"], "longitude": sensor["longitude"], "intensity": int(data_split[2]), "radius": 0.0, "sensor": serv_address + ":" + str(serv_port) + "/sensors/" + str(sensor["id"]) + "/", "trucks": []}
						to_post_to = serv_address + ":" + str(serv_port) + "/fires/"
						print(to_post_to)
						fire = json.dumps(fire).replace("'",'"')
						print(fire)
						print("Posting the fire...")
						post_req = requests.post(to_post_to, json = json.loads(fire))
						print("Request sent! Code: " + str(post_req.status_code))
					else:
						fire = fire[0]
						fire["intensity"] = int(data_split[2])
						to_update = fire["url"]
						# print(to_update)
						payload = fire
						# print(payload)
						print("Updating the fire...")
						update_req = requests.put(to_update, data=payload)
						print("Request sent! Code: " + str(update_req.status_code))
						# print(update_req.status_code)

					print("Sending to the MQTT...")
					mqtt_msg = "intensite,capteur=capteur" + data_split[1] + data_split[0] + " valeur=" + data_split[2]
					ret = mqtt_client.publish("sensors", mqtt_msg, 1)
					print(ret)
					print("Sending ACK...")
					msg = source_addr + message_types["ACK"] + connections[source_addr].encrypt(b"ACK:SUC")
				except nacl.exceptions.CryptoError:
					print("ERROR: decrypting error. Sending NACK...")
					msg = source_addr + message_types["NACK"] + b"ERROR 03 : Error while decrypting message data!"

		# The message will be forged in the previous conditions
		ser.write(msg)
		print("Message sent!")
		msg = ""