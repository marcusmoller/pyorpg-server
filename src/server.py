import time
import logging
import logging.handlers
import base64

# todo: gui
#from gui import ServerGUI
#from twisted.internet import gtk2reactor
#gtk2reactor.install()

# twisted
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
    # start gui
    #serverGUI = ServerGUI()

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

    g.serverLogger.info('Spawning map NPCs...')
    spawnAllMapNpcs()

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

    g.serverLogger.info('Loading NPCs...')
    loadNpcs()

    g.serverLogger.info('Loading items...')
    loadItems()

    g.serverLogger.info('Loading classes...')
    loadClasses()

    g.serverLogger.info('Loading maps...')
    loadMaps()

    g.serverLogger.info('Loading spells...')
    loadSpells()

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

        # handle base64 data
        decodedData = base64.b64decode(data)

        g.connectionLogger.debug("Received data from " + str(self.transport.getPeer().host))
        g.connectionLogger.debug(" -> " + decodedData)

        dataHandler.handleData(clientIndex, decodedData)

    def closeConnection(self, index):
        ''' closes connection with client #index '''
        print 'closeConnection() todo'

    def sendDataTo(self, index, data):
        # encode data using base64
        encodedData = base64.b64encode(data)
        self.factory.clients[index].sendLine(encodedData)

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
lastRegenNpcHp = 0

def serverLoop():
    global clockTick, tmr500, tmr1000, lastUpdatePlayerVitals, lastUpdateSavePlayers, lastUpdateMapSpawnItems

    clockTick = time.time() * 1000

    if clockTick > tmr500:
        # check for disconnects

        # process ai
        updateNpcAi()

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

    # loop the serverLoop function every half second
    reactor.callLater(0.5, serverLoop)

def updateNpcAi():
    global lastRegenNpcHp
    didWalk = False

    for i in range(MAX_MAPS):
        if playersOnMap[i] == 1:
            tickCount = time.time()

            for j in range(MAX_MAP_NPCS):
                npcNum = mapNPC[i][j].num

                # attacking on sight
                if Map[i].npc[j] != None and mapNPC[i][j].num != None:
                    # if npc behavior is attack on sight, search for player on map
                    if NPC[npcNum].behaviour == NPC_BEHAVIOUR_ATTACKONSIGHT or NPC[npcNum].behaviour == NPC_BEHAVIOUR_GUARD:
                        for plr in range(g.totalPlayersOnline):
                            if getPlayerMap(g.playersOnline[plr]) == i:
                                if mapNPC[i][j].target is None:
                                    if getPlayerAccess(g.playersOnline[plr]) <= ADMIN_MONITOR:
                                        n = NPC[npcNum].range

                                        # calculate the distance between npc and player
                                        deltaX = abs(mapNPC[i][j].x - getPlayerX(g.playersOnline[plr]))
                                        deltaY = abs(mapNPC[i][j].y - getPlayerY(g.playersOnline[plr]))

                                        # are they in range? if so attack
                                        if deltaX <= n and deltaY <= n:
                                            if NPC[npcNum].behaviour == NPC_BEHAVIOUR_ATTACKONSIGHT: #or getplayerpk == yes
                                                if len(NPC[npcNum].attackSay) > 0:
                                                    playerMsg(g.playersOnline[plr], 'A ' + NPC[npcNum].name + ' says, ' + NPC[npcNum].attackSay + ' to you.', sayColor)

                                                # set player as target
                                                mapNPC[i][j].target = g.playersOnline[plr]


                # npc walking/targetting
                # todo: better ai movement
                if Map[i].npc[j] != None:
                    if mapNPC[i][j].num != None:
                        target = mapNPC[i][j].target

                        # check if its time for the npc to walk
                        if NPC[npcNum].behaviour != NPC_BEHAVIOUR_SHOPKEEPER:

                            # check if following a player
                            if target != None:
                                if isPlaying(target) and getPlayerMap(target) == i:

                                    if not didWalk:
                                        # move the npc
                                        rnd = random.randint(0, 3)

                                        if rnd == 0:
                                            # up
                                            if mapNPC[i][j].y > getPlayerY(target):
                                                if canNpcMove(i, j, DIR_UP):
                                                    npcMove(i, j, DIR_UP, MOVING_WALKING)
                                                    didWalk = True

                                            # down
                                            elif mapNPC[i][j].y < getPlayerY(target):
                                                if canNpcMove(i, j, DIR_DOWN):
                                                    npcMove(i, j, DIR_DOWN, MOVING_WALKING)
                                                    didWalk = True

                                            # left
                                            elif mapNPC[i][j].x > getPlayerX(target):
                                                if canNpcMove(i, j, DIR_LEFT):
                                                    npcMove(i, j, DIR_LEFT, MOVING_WALKING)
                                                    didWalk = True

                                            # right
                                            elif mapNPC[i][j].x < getPlayerX(target):
                                                if canNpcMove(i, j, DIR_RIGHT):
                                                    npcMove(i, j, DIR_RIGHT, MOVING_WALKING)
                                                    didWalk = True

                                        elif rnd == 1:
                                            # right
                                            if mapNPC[i][j].x < getPlayerX(target):
                                                if canNpcMove(i, j, DIR_RIGHT):
                                                    npcMove(i, j, DIR_RIGHT, MOVING_WALKING)
                                                    didWalk = True

                                            # left
                                            elif mapNPC[i][j].x > getPlayerX(target):
                                                if canNpcMove(i, j, DIR_LEFT):
                                                    npcMove(i, j, DIR_LEFT, MOVING_WALKING)
                                                    didWalk = True

                                            # down
                                            elif mapNPC[i][j].y < getPlayerY(target):
                                                if canNpcMove(i, j, DIR_DOWN):
                                                    npcMove(i, j, DIR_DOWN, MOVING_WALKING)
                                                    didWalk = True

                                            # up
                                            elif mapNPC[i][j].y > getPlayerY(target):
                                                if canNpcMove(i, j, DIR_UP):
                                                    npcMove(i, j, DIR_UP, MOVING_WALKING)
                                                    didWalk = True

                                        elif rnd == 2:
                                            # down
                                            if mapNPC[i][j].y < getPlayerY(target):
                                                if canNpcMove(i, j, DIR_DOWN):
                                                    npcMove(i, j, DIR_DOWN, MOVING_WALKING)
                                                    didWalk = True

                                            # up
                                            elif mapNPC[i][j].y > getPlayerY(target):
                                                if canNpcMove(i, j, DIR_UP):
                                                    npcMove(i, j, DIR_UP, MOVING_WALKING)
                                                    didWalk = True

                                            # right
                                            elif mapNPC[i][j].x < getPlayerX(target):
                                                if canNpcMove(i, j, DIR_RIGHT):
                                                    npcMove(i, j, DIR_RIGHT, MOVING_WALKING)
                                                    didWalk = True

                                            # left
                                            elif mapNPC[i][j].x > getPlayerX(target):
                                                if canNpcMove(i, j, DIR_LEFT):
                                                    npcMove(i, j, DIR_LEFT, MOVING_WALKING)
                                                    didWalk = True

                                        elif rnd == 3:
                                            # left
                                            if mapNPC[i][j].x > getPlayerX(target):
                                                if canNpcMove(i, j, DIR_LEFT):
                                                    npcMove(i, j, DIR_LEFT, MOVING_WALKING)
                                                    didWalk = True

                                            # right
                                            elif mapNPC[i][j].x < getPlayerX(target):
                                                if canNpcMove(i, j, DIR_RIGHT):
                                                    npcMove(i, j, DIR_RIGHT, MOVING_WALKING)
                                                    didWalk = True

                                            # up
                                            elif mapNPC[i][j].y > getPlayerY(target):
                                                if canNpcMove(i, j, DIR_UP):
                                                    npcMove(i, j, DIR_UP, MOVING_WALKING)
                                                    didWalk = True

                                            # down
                                            elif mapNPC[i][j].y < getPlayerY(target):
                                                if canNpcMove(i, j, DIR_DOWN):
                                                    npcMove(i, j, DIR_DOWN, MOVING_WALKING)
                                                    didWalk = True

                                    # check if we cant move and if player is behind something and if we can just switch directions
                                    if not didWalk:
                                        if mapNPC[i][j].x - 1 == getPlayerX(target) and mapNPC[i][j].y == getPlayerY(target):
                                            if mapNPC[i][j].dir != DIR_LEFT:
                                                npcDir(i, j, DIR_LEFT)
                                                didWalk = True

                                        if mapNPC[i][j].x + 1 == getPlayerX(target) and mapNPC[i][j].y == getPlayerY(target):
                                            if mapNPC[i][j].dir != DIR_RIGHT:
                                                npcDir(i, j, DIR_RIGHT)
                                                didWalk = True

                                        if mapNPC[i][j].x == getPlayerX(target) and mapNPC[i][j].y - 1 == getPlayerY(target):
                                            if mapNPC[i][j].dir != DIR_UP:
                                                npcDir(i, j, DIR_UP)
                                                didWalk = True

                                        if mapNPC[i][j].x == getPlayerX(target) and mapNPC[i][j].y + 1 == getPlayerY(target):
                                            if mapNPC[i][j].dir != DIR_DOWN:
                                                npcDir(i, j, DIR_DOWN)
                                                didWalk = True

                                        if not didWalk:
                                            # still couldnt move, so walk randomly
                                            rnd = random.randint(0, 1)

                                            if rnd == 1:
                                                rnd = random.randint(0, 3)

                                                if canNpcMove(i, j, rnd):
                                                    npcMove(i, j, rnd, MOVING_WALKING)

                                else:
                                    mapNPC[i][j].target = None

                            else:
                                k = random.randint(0, 3)

                                if k == 1:
                                    k = random.randint(0, 3)

                                    if canNpcMove(i, j, k):
                                        npcMove(i, j, k, MOVING_WALKING)

                # npc attacking
                if Map[i].npc[j] != None and mapNPC[i][j].num != None:
                    target = mapNPC[i][j].target

                    # check if npc can attack targeted player
                    if target != None:
                        if isPlaying(target) and getPlayerMap(target) == i:
                            # can npc attack player?
                            if canNpcAttackPlayer(j, target):
                                # can player block
                                if not canPlayerBlockHit(target):
                                    damage = NPC[npcNum].stat[Stats.strength] - getPlayerProtection(target)
                                    npcAttackPlayer(j, target, damage)

                                else:
                                    playerMsg(target, 'Your ' + Item[getPlayerInvItemNum(target, getPlayerEquipmentSlot(target, Equipment.shield))].name + ' blocks the hit!', textColor.BRIGHT_CYAN)
                        
                        else:
                            mapNPC[i][j].target = None

                # npc regen hp
                if mapNPC[i][j].num is not None:
                    if tickCount > lastRegenNpcHp + 10000:
                        if mapNPC[i][j].vital[Vitals.hp] > 0:
                            mapNPC[i][j].vital[Vitals.hp] += getNpcVitalRegen(npcNum, Vitals.hp)

                            # check if they have more than they should, then set it to max
                            if mapNPC[i][j].vital[Vitals.hp] > getNpcMaxVital(npcNum, Vitals.hp):
                                mapNPC[i][j].vital[Vitals.hp] = getNpcMaxVital(npcNum, Vitals.hp)

                    lastRegenNpcHp = tickCount

                # npc spawning
                if mapNPC[i][j].num is None:
                    if Map[i].npc[j] is not None:
                        if time.time() * 1000 > mapNPC[i][j].spawnWait + NPC[Map[i].npc[j]].spawnSecs * 1000:
                            spawnNpc(j, i)


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
