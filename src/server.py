import time
import logging
import logging.handlers

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

from gamelogic import *
from datahandler import *
from database import *
from objects import *
import globalvars as g

dataHandler = None


def startServer():
    # start logging
    setupLogging()

    # start server
    global dataHandler

    startTime = time.time()

    g.serverLogger.info("Starting server...")

    factory = gameServerFactory()
    reactor.listenTCP(2727, factory)
    g.conn = factory.protocol(factory)

    loadGameData()

    g.serverLogger.info("Spawning map items...")
    spawnAllMapsItems()

    g.serverLogger.info("Creating map cache...")
    createFullMapCache()

    dataHandler = DataHandler()

    endTime = time.time()
    totalTime = (endTime - startTime)*1000
    g.serverLogger.info("Initialization complete. Server loaded in " + str(round(totalTime, 2)) + " ms.")

    # start the server loop and the reactor
    serverLoop()
    reactor.run()


def setupLogging():
    ''' setup loggers for server (general) and connection (in/out) '''
    ''' max log size is 1mb '''
    # stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s (%(name)s) %(levelname)s: %(message)s'))

    # file handler
    fh = logging.handlers.RotatingFileHandler(filename='../server.log', maxBytes=1048576, backupCount=5)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s (%(name)s) %(levelname)s: %(message)s'))

    g.serverLogger = logging.getLogger('server')
    g.serverLogger.setLevel(logging.INFO)
    g.serverLogger.addHandler(ch)
    g.serverLogger.addHandler(fh)

    g.connectionLogger = logging.getLogger('connection')
    g.connectionLogger.setLevel(logging.INFO)
    g.connectionLogger.addHandler(ch)
    g.connectionLogger.addHandler(fh)


def loadGameData():
    setupDatabase()

    g.serverLogger.info('Loading items...')
    loadItems()

    g.serverLogger.info('Loading classes...')
    loadClasses()

    g.serverLogger.info('Loading maps...')
    loadMaps()

    for i in range(MAX_PLAYERS):
        clearPlayer(i)


class gameServerProtocol(LineReceiver):
    MAX_LENGTH = 999999 #todo: find a suitable size (see client: sendMap (in clienttcp.py))

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)
        g.connectionLogger.info("CONNECTION - Connection from IP: " + str(self.transport.getPeer().host))

    def connectionLost(self, reason):
        clientIndex = self.factory.clients.index(self)
        self.transport.loseConnection()
        closeConnection(clientIndex)

        self.factory.clients.remove(self)

    def lineReceived(self, data):
        global dataHandler
        clientIndex = self.factory.clients.index(self)

        g.connectionLogger.debug("Received data from " + str(self.transport.getPeer().host))
        g.connectionLogger.debug(" -> " + data)

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
            try:
                if getPlayerMap(g.playersOnline[i]) == mapNum:
                    self.sendDataTo(i, data)
            except:
                # havent logged in yet
                continue

    def sendDataToMapBut(self, mapNum, index, data):
        for i in range(g.totalPlayersOnline):
            if getPlayerMap(g.playersOnline[i]) == mapNum:
                if g.playersOnline[i] != index:
                    self.sendDataTo(g.playersOnline[i], data)


class gameServerFactory(Factory):
    protocol = gameServerProtocol

    def __init__(self):
        self.clients = []

    def buildProtocol(self, addr):
        p = self.protocol(self)
        p.factory = self
        return p

# server loop and timings
clockTick = 0
tmr500 = 0
tmr1000 = 0
lastUpdatePlayerVitals = 0
lastUpdateMapSpawnItems = 0
lastUpdateSavePlayers = 0

def serverLoop():
    global clockTick, tmr500, tmr1000, lastUpdatePlayerVitals, lastUpdateSavePlayers, lastUpdateMapSpawnItems

    clockTick = time.time() * 1000

    if clockTick > tmr500:
        # check for disconnects

        # process ai
        tmr500 = time.time() * 1000 + 500

    if clockTick > tmr1000:
        # handle shutting down server

        # handle closing doors

        tmr1000 = time.time() * 1000 + 1000

    # update player vitals every 5 seconds
    if clockTick > lastUpdatePlayerVitals:
        updatePlayerVitals()
        lastUpdatePlayerVitals = time.time() * 1000 + 5000

    # spawn map items every 5 minutes
    if clockTick > lastUpdateMapSpawnItems:
        updateMapSpawnItems()
        lastUpdateMapSpawnItems = time.time() * 1000 + 300000

    # save players every 10 minutes
    if clockTick > lastUpdateSavePlayers:
        updateSavePlayers()
        lastUpdateSavePlayers = time.time() * 1000 + 600000

    # loop the serverLoop function every second
    reactor.callLater(1./1000, serverLoop)

def updatePlayerVitals():
    for i in range(g.totalPlayersOnline):
        if getPlayerVital(g.playersOnline[i], Vitals.hp) != getPlayerMaxVital(g.playersOnline[i], Vitals.hp):
            setPlayerVital(g.playersOnline[i], Vitals.hp, getPlayerVital(g.playersOnline[i], Vitals.hp) + getPlayerVitalRegen(g.playersOnline[i], Vitals.hp))
            sendVital(g.playersOnline[i], Vitals.hp)

        if getPlayerVital(g.playersOnline[i], Vitals.mp) != getPlayerMaxVital(g.playersOnline[i], Vitals.mp):
            setPlayerVital(g.playersOnline[i], Vitals.mp, getPlayerVital(g.playersOnline[i], Vitals.mp) + getPlayerVitalRegen(g.playersOnline[i], Vitals.mp))
            sendVital(g.playersOnline[i], Vitals.mp)

        if getPlayerVital(g.playersOnline[i], Vitals.sp) != getPlayerMaxVital(g.playersOnline[i], Vitals.sp):
            setPlayerVital(g.playersOnline[i], Vitals.sp, getPlayerVital(g.playersOnline[i], Vitals.sp) + getPlayerVitalRegen(g.playersOnline[i], Vitals.sp))
            sendVital(g.playersOnline[i], Vitals.sp)

def updateMapSpawnItems():
    for i in range(MAX_MAPS):
        # make sure no one is on the map when it respawns
        if not playersOnMap[i]:
            # clear unnecassary junk
            for j in range(MAX_MAP_ITEMS):
                clearMapItem(j, i)

            # spawn items
            spawnMapItems(i)
            sendMapItemsToAll(i)


def updateSavePlayers():
    if g.totalPlayersOnline > 0:
        g.serverLogger.info("Saving all players..")

        for i in range(g.totalPlayersOnline):
            savePlayer(i)

        g.serverLogger.info("Saved all players")
