from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, stdio
from twisted.protocols.basic import LineReceiver

import sys
import time

from gamelogic import *
from datahandler import *
from database import *
from objects import *
import globalvars as g

dataHandler = None

def startServer():
	global dataHandler

	startTime = time.time()

	log("Starting server...")

	loadGameData()

	log("Creating map cache...")
	createFullMapCache()

	factory = gameServerFactory()

	reactor.listenTCP(2727, factory)

	g.conn = factory.protocol(factory)

	dataHandler = DataHandler()

	endTime = time.time()
	totalTime = (endTime - startTime)*1000
	log("Initialization complete. Server loaded in " + str(round(totalTime, 2)) + " ms.")
	reactor.run()

def loadGameData():
	log("Loading classes...")
	loadClasses()

	log("Loading maps...")
	loadMaps()

	for i in range(MAX_PLAYERS):
		clearPlayer(i)


class gameServerProtocol(LineReceiver):
	MAX_LENGTH = 999999 #todo: find a suitable size (see client: sendMap (in clienttcp.py))
	
	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.factory.clients.append(self)
		log("CONNECTION - Connection from " + str(self.transport.getHost()))

	def connectionLost(self, reason):
		clientIndex = self.factory.clients.index(self)
		closeConnection(clientIndex)
		
		self.factory.clients.remove(self)

	def lineReceived(self, data):
		global dataHandler
		clientIndex = self.factory.clients.index(self)

		log("Received data from " + str(self.transport.getHost()))
		log(" -> " + data)

		# DEBUG
		if data == "debug":
			print Player[55].Password
			return

		dataHandler.handleData(clientIndex, data)

	def sendDataTo(self, index, data):
		self.factory.clients[index].sendLine(data)

	def sendDataToAll(self, data):
		for i in range(0, len(self.factory.clients)):
			self.sendDataTo(i, data)

	def sendDataToAllBut(self, index, data):
		for i in range(0, len(self.factory.clients)):
			if i == index:
				continue
			else:
				self.sendDataTo(i, data)

	def sendDataToMap(self, mapNum, data):
		for i in range(0, len(self.factory.clients)):
			if getPlayerMap(g.playersOnline[i]) == mapNum:
				self.sendDataTo(i, data)


class gameServerFactory(Factory):
	protocol = gameServerProtocol
	def __init__(self):
		self.clients = []

	def buildProtocol(self, addr):
		p = self.protocol(self)
		p.factory = self
		return p

def updateSavePlayers():
	if g.totalPlayersOnline > 0:
		log("Saving all players..")

		for i in range(g.totalPlayersOnline):
			savePlayer(i)

		log("Saved all players")