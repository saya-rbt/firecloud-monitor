# coding: utf-8
# author: @sayabiws
# Script to generate the grid depending on the coordinates and the zone we want to cover

import requests
import json

url = "http://192.168.0.10:8001/sensors/"

# Dardilly
startlat = 45.807710
startlng = 4.752261

# St-Priest
endlat = 45.688500
endlng = 4.956433
xinit = 0
yinit = 0

difflat = (endlat - startlat)/6
difflng = (endlng - startlng)/10

# payload = {"posx": xinit, "posy": yinit, "latitude": startlat, "longitude": startlng}
payload = {}

for y in range(6):
	for x in range(10):
		payload["posx"] = x
		payload["posy"] = y
		payload["latitude"] = startlat + (difflat*y)
		payload["longitude"] = startlng + (difflng*x)
		to_send = json.dumps(payload).replace("'", '"')
		print(type(to_send))
		print(to_send)
		r = requests.post(url, json=json.loads(to_send))
		print(r.status_code)