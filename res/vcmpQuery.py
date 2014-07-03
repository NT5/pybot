__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$22-Jun-2012 15:51:16$"

###############################################################
# sampQuery.py
# Version 1.1
# This class connects to a specific SA-MP server via sockets.
# Copyright 2012 Edward McKnight (EM-Creations.co.uk)
# Creative Commons Attribution-NoDerivs 3.0 Unported License
###############################################################

# Edited for VCMP

import socket
import struct

class vcmpQuery:

	def __init__(self, sock=None, server="127.0.0.1", port=5192, timeout = 2, gamepacket = 'VCMP'):
		self.timeout = timeout
		self.gamepacket = gamepacket
		if sock is None:
			self.serverVars = [server, port]
		else:
			self.sock = sock

	def connect(self):
		try:
			self.serverVars[0] = socket.gethostbyname(self.serverVars[0])
			socket.setdefaulttimeout(self.timeout)
			self.sock = socket.socket(
			socket.AF_INET, socket.SOCK_DGRAM) # Internet and UDP
		except socket.gaierror:
			return False

		packet = self.assemblePacket("p0101")

		try:
			self.send(packet)

			reply = self.receive()[10:]

			if reply == 'p0101':
				return True
			else:
				return False
		except socket.timeout:
			return False


	def send(self, msg):
		self.sock.sendto(msg, (self.serverVars[0], self.serverVars[1]))


	def receive(self, buffer=1024):
		msg = self.sock.recv(buffer)
		return msg


	def close(self):
		self.sock.close()


	def getInfo(self): # Finished
		"""Returns a dictionary containing server information:
		{
			'password' : integer,
			'players' : integer,
			'maxplayers' : integer,
			'hostname' : string,
			'gamemode' : string,
			'mapname' : string,
		}"""
		packet = self.assemblePacket("i")
		self.send(packet)

		reply = self.receive()

		reply = reply[11:]

		serverInfo = {'password' : 0, 'players' : 0, 'maxplayers' : 0, 'hostname' : "", 'gamemode' : "", 'mapname' : ""}

		serverInfo['password'] = ord(reply[0:1])

		players = struct.unpack("<h", reply[1:3])

		serverInfo['players'] = players[0];

		maxPlayers = players = struct.unpack("<h", reply[3:5])

		serverInfo['maxplayers'] = maxPlayers[0];

		reply = reply[5:] # Clean up bytes

		strLen = struct.unpack("<i", reply[0:4])

		serverInfo['hostname'] = reply[4:(strLen[0]+4)]

		reply = reply[(strLen[0]+4):] # Clean up bytes

		strLen = struct.unpack("<i", reply[0:4])

		serverInfo['gamemode'] = reply[4:(strLen[0]+4)]

		reply = reply[(strLen[0]+4):] # Clean up bytes

		strLen = struct.unpack("<i", reply[0:4])

		serverInfo['map'] = reply[4:(strLen[0]+4)]

		return serverInfo


	def getBasicPlayers(self): # Finished
		"""Returns a list containing a dictionary for each player:
		[
			{
				'name' : string,
				'score' : integer,
			},
			{
				'name' : string,
				'score' : integer,
			},
		]
		Note: This will return an empty list if the player count is above 100."""
		packet = self.assemblePacket("c")
		self.send(packet)

		reply = self.receive()
		reply = reply[11:] # Clean up bytes
		players = []

		strLen = struct.unpack("<h", reply[0:2])
		playerCount = strLen[0]

		reply = reply[2:] # Clean up bytes

		for i in range(playerCount):
			players.append({'name' : '', 'score' : 0})

		pointer = 0

		for player in players:
			strLen = ord(reply[pointer:(pointer + 1)])

			name = reply[(pointer + 1):(pointer + (strLen + 1))]

			temp = struct.unpack("<i", reply[(pointer + (strLen + 1)):(pointer + (strLen + 5))])
			pointer += (strLen + 5)

			player['name'] = name
			player['score'] = temp[0]

		return players


	def getDetailedPlayers(self): # Finished
		"""Returns a list containing a dictionary for each player:
		[
			{
				'id' : integer,
				'name' : string,
				'score' : integer,
				'ping' : integer,
			},
			{
				'id' : integer,
				'name' : string,
				'score' : integer,
				'ping' : integer,
			},
		]
		Note: This will return an empty list if the player count is above 100."""
		packet = self.assemblePacket("d")
		self.send(packet)

		reply = self.receive()
		reply = reply[11:] # Clean up bytes
		players = []

		strLen = struct.unpack("<h", reply[0:2])
		playerCount = strLen[0]

		reply = reply[2:] # Clean up bytes

		for i in range(playerCount):
			players.append({'id' : 0, 'name' : '', 'score' : 0, 'ping' : 0})

		pointer = 0

		for player in players:
			id = ord(reply[pointer:(pointer + 1)])

			strLen = ord(reply[(pointer + 1):(pointer + 2)])

			name = reply[(pointer + 2):(pointer + (strLen + 2))]

			score = struct.unpack("<i", reply[(pointer + (strLen + 2)):(pointer + (strLen + 6))])

			ping = struct.unpack("<i", reply[(pointer + (strLen + 6)):(pointer + (strLen + 10))])

			pointer += (strLen + 10)

			player['id'] = id
			player['name'] = name
			player['score'] = score[0]
			player['ping'] = ping[0]

		return players


	def getRules(self): # Finished
		"""Returns a list containing a dictionary for each rule:
		[
			{
				'rule' : string,
				'value' : integer,
			},
			{
				'rule' : string,
				'value' : integer,
			},
		]"""
		packet = self.assemblePacket("r")
		self.send(packet)

		reply = self.receive()
		reply = reply[11:] # Clean up bytes
		rules = []

		strLen = struct.unpack("<h", reply[0:2])
		ruleCount = strLen[0]

		reply = reply[2:] # Clean up bytes

		for i in range(ruleCount):
			rules.append({'rule' : '', 'value' : ''})

		pointer = 0

		for rule in rules:
			strLen = ord(reply[pointer:(pointer + 1)])

			name = reply[(pointer + 1):(pointer + (strLen + 1))]

			strLenVal = ord(reply[(pointer + (strLen + 1)):(pointer + (strLen + 2))])

			value = reply[(pointer + (strLen + 2)):(pointer + ((strLen + strLenVal) + 2))]

			pointer += ((strLen + strLenVal) + 2)

			rule['rule'] = name
			rule['value'] = value

		return rules


	def assemblePacket(self, type):
		ipSplit = str.split(self.serverVars[0], '.')

		packet = self.gamepacket
		packet += chr(int(ipSplit[0]))
		packet += chr(int(ipSplit[1]))
		packet += chr(int(ipSplit[2]))
		packet += chr(int(ipSplit[3]))
		packet += chr(self.serverVars[1] & 0xFF)
		packet += chr(self.serverVars[1] >> 8 & 0xFF)
		packet += type

		return packet


def new(server="127.0.0.1", port=7777):
	"""Creates a new sampQuery object, if an address isn't passed 127.0.0.1 is used. If a port isn't passed 7777 is used."""
	return vcmpQuery(None, server, port)