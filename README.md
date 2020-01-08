# Firecloud Monitor

*IoT fire simulation and monitoring cloud platform for a school project*

## The project

The project is split in two parts: **Simulation** and **Emergency**.

The global idea is that the *Simulation* will be creating fake fires (by choosing coordinates, intensity of the fire, and add them a timestamp) through the *Simulator*, who will be sent to a web service REST API (the "*simulation server*"), who will then send the fire informations through a STREAM API (via WebSockets) to a sensors station (in our example a Raspberry Pi, but it can be anything), who will then send them to a [Techno-Innov RF-Sub1GHz](http://www.techno-innov.fr/) through USB.

Then, the *Emergency* system (which is basically a fire station control center) will collect the informations about the fire from another RF-Sub1GHz microcontroller through radio, before transferring it to the *data collect station* (again, it can be on a Raspberry Pi). The data collect will then send those informations to 2 different places:

* The **Dashboard**: The dashboard will handle the data and send it to an [InfluxDB](https://www.influxdata.com/) database, and use [Mosquitto](https://mosquitto.org/) and [Grafana](https://grafana.com/) to display it on a web interface, which can be used to visualize statistics about the fires.
* The **Emergency Web Server**: It's a Django-based server which will insert the fire into a PostgreSQL database, before transmitting it to the **Emergency Manager**. The web server is also used to offer a web interface with a map (the *Emergency View*), using [Leaflet](https://leafletjs.com/), to visualize the fire and firetrucks locations gotten from the database for the fire stations to use them in their control rooms or something.

The role of the **Emergency Manager** will be, whenever info about a fire is sent to it, to decide which firetrucks should be sent to deal with it. The intensity of a fire ranges from 0 (no fire or extinguished) to 9 (*absolute inferno hellfire*), while firetrucks have different extinguishing powers, ranging from 1 (water pistol) to 9 (~~*Blastoise*~~). The extinguishing powers of the trucks working on a fire should be at least higher than the fire intensity in order to make it slowly decrease. After choosing which trucks it will send, it starts a mission, that will then be inserted into the database. The *Simulator* then queries the database about whether firetrucks have been sent to deal with the fire or not, and decides to either rise the fire's intensity if no trucks are there yet, or to lower it if there are enough to cover it. Then, it sends updated information through the API again to the sensors, to the data collecting station, to the emergency web server again, who will update the database (*it is important to note that the Simulator **never** writes into the database itself, it only reads*) and warn the *Emergency Manager* about the progress being made on the fire. This goes on until the fire is eventually extinguished. If it is possible to free a firetruck before the fire is extinguished (ie. the fire's intensity has been lowered to a level that can be handled by less trucks than there currently are on it), the *Emergency Manager* can call the unnecessary trucks back to the station.

When the fire is extinguished, the *Emergency Manager* will end the mission and call all the firetrucks on it back to the fire stations.

## The network infrastructure

![The topology](https://github.com/sayabiws/firecloud-monitor/blob/master/docs/diagrams/network-topology.png)

Every service is self-hosted in the DMZ in the datacenter we're creating with Docker.

The web clients, seeing the *Emergency View*, are in the different fire stations (`SDIS-1` and `SDIS-2`).

## The applicative structure

![Application diagram](https://github.com/sayabiws/firecloud-monitor/blob/master/docs/diagrams/application-structure-diagram.png)

Everything in blue is server-side, everything in orange is client-side.

*Note: we're using a single Raspberry Pi for both microcontrollers.*

## The IoT protocol

The IoT protocol is based on UDP, though it's been slightly modified to handle a "*message type*" flag as well as use 1-byte addresses instead of IP addresses. A whole byte isn't necessary, but allows for evolution. Here is a representation of a packet:

| Byte |   0    |      1       |
|:----:|:------:|:------------:|
|  0   | Length | Destination  |
|  2   | Source | Message type |
| 4-62 |  Data  | Data (cont.) |

And here is the table of the current message types (can be expanded later):

|   Value   |                  Message type                  |
|:---------:|:----------------------------------------------:|
|   0x01    |     HELLO (Sensors warn of their presence)     |
|   0x02    |          THERE (Data collect respond)          |
|   0x03    |                      DATA                      |
|   0x04    |                      ACK                       |
|   0x05    | NACK (transmission error, send the data again) |
| 0x06-0xFF |       Undefined, reserved for future use       |

## The team

|                  Member                   |                                    Role                                     |
|:-----------------------------------------:|:---------------------------------------------------------------------------:|
| [@sayabiws](https://github.com/sayabiws/) |             IoT (RF-Sub1GHz), Dashboard (InfluxDB, Grafana...)              |
| [@SirLewis](https://github.com/SirLewis)  | Django web servers and APIs, PostgreSQL DB, Simulator and Emergency Manager |
|   [@empyrz](https://github.com/empyrz)    |                    Servers, Docker, Dashboard, Big Data                     |
| [@LucasCPE](https://github.com/LucasCPE)  |                          Network, servers, Docker                           |

The different functionalities to develop are in tracked in the [Fireboard](https://github.com/sayabiws/firecloud-monitor/projects/1).