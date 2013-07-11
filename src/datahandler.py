from database import *
from packettypes import *
from gamelogic import *
from objects import *
from constants import *
from utils import *
import globalvars as g

#debug
import time

class DataHandler():
    def handleData(self, index, data):
        jsonData = decodeJSON(data)
        packetType = jsonData[0]["packet"]

        if packetType == ClientPackets.CGetClasses:
            self.handleGetClasses(index)

        elif packetType == ClientPackets.CNewAccount:
            self.handleNewAccount(index, jsonData)

        elif packetType == ClientPackets.CLogin:
            self.handleLogin(index, jsonData)

        elif packetType == ClientPackets.CAddChar:
            self.handleAddChar(index, jsonData)

        elif packetType == ClientPackets.CUseChar:
            self.handleUseChar(index, jsonData)

        elif packetType == ClientPackets.CSayMsg:
            self.handleSayMsg(index, jsonData)

        elif packetType == ClientPackets.CPlayerMsg:
            self.handlePlayerMsg(index)

        elif packetType == ClientPackets.CPlayerMove:
            self.handlePlayerMove(index, jsonData)

        elif packetType == ClientPackets.CPlayerDir:
            self.handlePlayerDir(index, jsonData)

        elif packetType == ClientPackets.CAttack:
            self.handleAttack(index)

        elif packetType == ClientPackets.CWarpMeTo:
            self.handleWarpMeTo(index, jsonData)

        elif packetType == ClientPackets.CWarpToMe:
            self.handleWarpToMe(index, jsonData)

        elif packetType == ClientPackets.CWarpTo:
            self.handleWarpTo(index, jsonData)

        elif packetType == ClientPackets.CSetSprite:
            self.handleSetSprite(index, jsonData)

        elif packetType == ClientPackets.CRequestNewMap:
            self.handleRequestNewMap(index, jsonData)

        elif packetType == ClientPackets.CMapData:
            self.handleMapData(index, jsonData)

        elif packetType == ClientPackets.CNeedMap:
            self.handleNeedMap(index, jsonData)

        elif packetType == ClientPackets.CWhosOnline:
            self.handleWhosOnline(index)

        elif packetType == ClientPackets.CRequestEditMap:
            self.handleRequestEditMap(index)

        elif packetType == ClientPackets.CRequestEditItem:
            self.handleRequestEditItem(index)

        elif packetType == ClientPackets.CSaveItem:
            self.handleSaveItem(index, jsonData)

        elif packetType == ClientPackets.CSetAccess:
            self.handleSetAccess(index, jsonData)

        elif packetType == ClientPackets.CGiveItem:
            self.handleGiveItem(index, jsonData)

        elif packetType == ClientPackets.CQuit:
            self.handleQuit(index)

        else:
            # Packet is unknown - hacking attempt
            print "hacking attempt"

    def handleGetClasses(self, index):
        if not isPlaying(index):
            sendNewCharClasses(index)

    def handleNewAccount(self, index, jsonData):
        name = jsonData[0]['name']
        password = jsonData[0]['password']

        if not isPlaying(index):
            if not isLoggedIn(index):
                # prevent hacking
                if len(name) < 3 or len(password) < 3:
                    print "hacking attempt"
                    alertMsg(index, "Your name and password must be at least three characters in length.")
                    return

                # check if account already exists
                if not accountExists(name):
                    addAccount(index, name, password)
                    g.serverLogger.info('Account ' + name + ' has been created')
                    alertMsg(index, "Your account has been created!")
                else:
                    g.serverLogger.info('Account name has already been taken!')
                    alertMsg(index, "Sorry, that account name is already taken!")

    ''' Player login '''
    def handleLogin(self, index, jsonData):
        if not isPlaying(index):
            if not isLoggedIn(index):

                plrName = jsonData[0]["name"]
                plrPassword = jsonData[0]["password"]

                # todo: check version

                # todo: is shutting down?

                if len(plrName) < 3 or len(plrPassword) < 3:
                    #alert msg
                    return

                if not accountExists(plrName):
                    # alert msg
                    return

                if not passwordOK(plrName, plrPassword):
                    # alert msg
                    return

                if isMultiAccounts(plrName):
                    # alert msg
                    return

                # load the player
                loadPlayer(index, plrName)
                sendChars(index)

                g.connectionLogger.info(getPlayerLogin(index) + ' has logged in')

    ''' player creates a new character '''
    def handleAddChar(self, index, jsonData):
        if not isPlaying(index):
            name = jsonData[0]["name"]
            sex = jsonData[0]["sex"]
            Class = jsonData[0]["class"]
            charNum = jsonData[0]["slot"]

            # prevent hacking
            if len(name) < 3:
                print "hacking alert (handleAddChar() too short name)"
                return

            #todo: check for certain letters


            if charNum < 0 or charNum > MAX_CHARS:
                print "hacking attempt (handleaddChar() invalid charnum)"
                return

            #todo: check sex

            if Class < 0 or Class > g.maxClasses:
                print "hacking attempt (handleaddChar() invalid class)"
                return

            # check if a character already exists in slot
            if charExist(index, charNum):
                print "character slot already in use (handleaddchar())"
                return

            # check if name is in use
            if findChar(name):
                print "name already in use"
                return

            # everything went ok, add the character
            addChar(index, name, sex, Class, charNum)
            g.serverLogger.info("Character " + name + " added to " + getPlayerLogin(index) + "'s account.")
            # alertMsg(player created)

            # send characters to player
            sendChars(index)


    ''' Player selected character '''
    def handleUseChar(self, index, jsonData):
        if not isPlaying(index):
            charNum = jsonData[0]["charslot"]

            if charNum < 0 or charNum > MAX_CHARS:
                print "hacking attempt (handleUseChar)"
                return

            # make sure character exists
            if charExist(index, charNum):
                TempPlayer[index].charNum = charNum
                joinGame(index)

                g.connectionLogger.info("Has begun playing")

    ''' say msg '''
    def handleSayMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        g.serverLogger.info('player said something D:')
        mapMsg(getPlayerMap(index), getPlayerName(index) + ': ' + msg, sayColor)

    ''' Player message '''
    def handlePlayerMsg(self, index):
        print "player msg"

    ''' Player movement '''
    def handlePlayerMove(self, index, jsonData):
        direction = jsonData[0]["direction"]
        movement = jsonData[0]["moving"]
        playerMove(index, direction, movement)

    ''' Player direction '''
    def handlePlayerDir(self, index, jsonData):
        direction = jsonData[0]["direction"]
        setPlayerDir(index, direction)
        sendPlayerDir(index)

    def handleAttack(self, index):
        # try to attack a player
        for i in range(g.totalPlayersOnline):
            tempIndex = g.playersOnline[i]

            # make sure we dont attack ourselves
            if tempIndex != index:
                # can we attack the player?
                if canAttackPlayer(index, tempIndex):
                    # todo: check if player can block hit

                    # get the damage we can do
                    # todo

                    attackPlayer(index, tempIndex, 5)

        # todo: handle attack npc

    def handleWarpMeTo(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt"
            return

        playerName = jsonData[0]['name']
        playerIndex = findPlayer(playerName)

        if playerIndex != index:
            if playerIndex is not None:
                playerWarp(index, getPlayerMap(playerIndex), getPlayerX(playerIndex), getPlayerY(playerIndex))
                playerMsg(playerIndex, getPlayerName(index) + ' has been warped to you.', textColor.BRIGHT_BLUE)
                playerMsg(index, 'You have been warped to ' + getPlayerName(playerIndex) + '.', textColor.BRIGHT_BLUE)
                g.connectionLogger.info(getPlayerName(index) + ' has warped to ' + getPlayerName(playerIndex) + ', map #' + str(getPlayerMap(index)))
            else:
                playerMsg(index, 'Player is not online.', textColor.RED) # white?
                return
        else:
            playerMsg(index, 'You cannot warp to yourself!', textColor.RED) # white?
            return

    def handleWarpToMe(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt"
            return

        playerName = jsonData[0]['name']
        playerIndex = findPlayer(playerName)

        if playerIndex != index:
            if playerIndex is not None:
                playerWarp(playerIndex, getPlayerMap(index), getPlayerX(index), getPlayerY(index))
                playerMsg(playerIndex, 'You have been summoned by ' + getPlayerName(index) + '.', textColor.BRIGHT_BLUE)
                playerMsg(index, getPlayerName(playerIndex) + ' has been summoned.', textColor.BRIGHT_BLUE)
                g.connectionLogger.info(getPlayerName(index) + ' has warped ' + getPlayerName(playerIndex) + ' to self, map #' + str(getPlayerMap(index)))
            else:
                playerMsg(index, 'Player is not online.', textColor.RED) # white?
                return
        else:
            playerMsg(index, 'You cannot warp to yourself!', textColor.RED) # white?
            return

    def handleWarpTo(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt"
            return

        mapNum = jsonData[0]['map']

        if mapNum < 0 or mapNum > MAX_MAPS:
            print "hacking attempt"
            return

        playerWarp(index, mapNum, getPlayerX(index), getPlayerY(index))
        playerMsg(index, 'You have been warped to map #' + str(mapNum), textColor.BRIGHT_BLUE)
        g.connectionLogger.info(getPlayerName(index) + ' warped to map #' + str(mapNum))

    def handleSetSprite(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt"
            return

        n = jsonData[0]["sprite"]

        setPlayerSprite(index, n)
        sendPlayerData(index)

    def handleRequestNewMap(self, index, jsonData):
        direction = jsonData[0]["direction"]

        if direction < DIR_UP or direction > DIR_RIGHT:
            print "hacking attempt"
            return

        playerMove(index, direction, 1)

    def handleMapData(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt - admin cloning"
            return

        mapNum = getPlayerMap(index)

        revision = Map[mapNum].revision + 1

        clearMap(mapNum)

        Map[mapNum].name = jsonData[0]["mapname"]
        Map[mapNum].revision = revision
        Map[mapNum].moral = jsonData[0]["moral"]
        Map[mapNum].tileSet = jsonData[0]["tileset"]
        Map[mapNum].up = jsonData[0]["up"]
        Map[mapNum].down = jsonData[0]["down"]
        Map[mapNum].left = jsonData[0]["left"]
        Map[mapNum].right = jsonData[0]["right"]
        Map[mapNum].bootMap = jsonData[0]["bootmap"]
        Map[mapNum].bootx = jsonData[0]["bootx"]
        Map[mapNum].booty = jsonData[0]["booty"]

        tile_i = 1
        #todo: fix [0]
        for x in range(MAX_MAPX):
            for y in range(MAX_MAPY):
                Map[mapNum].tile[x][y].ground = jsonData[tile_i][0]["ground"]
                Map[mapNum].tile[x][y].mask = jsonData[tile_i][0]["mask"]
                Map[mapNum].tile[x][y].anim = jsonData[tile_i][0]["animation"]
                Map[mapNum].tile[x][y].fringe = jsonData[tile_i][0]["fringe"]
                Map[mapNum].tile[x][y].type = jsonData[tile_i][0]["type"]
                Map[mapNum].tile[x][y].data1 = jsonData[tile_i][0]["data1"]
                Map[mapNum].tile[x][y].data2 = jsonData[tile_i][0]["data2"]
                Map[mapNum].tile[x][y].data3 = jsonData[tile_i][0]["data3"]

                tile_i += 1

        # save map
        saveMap(mapNum)
        mapCacheCreate(mapNum)

        # refresh map for everyone online
        for i in range(g.totalPlayersOnline):
            index = g.playersOnline[i]

            if isPlaying(index):
                if getPlayerMap(index) == mapNum:
                    playerWarp(index, mapNum, getPlayerX(index), getPlayerY(index))


        # todo: ALOT!

    def handleNeedMap(self, index, jsonData):
        g.serverLogger.debug("handleNeedMap()")
        answer = jsonData[0]["answer"]

        if answer == 1:
            # needs new revision
            sendMap(index, getPlayerMap(index))

        sendJoinMap(index)
        TempPlayer[index].gettingMap = False
        sendMapDone(index)

    def handleWhosOnline(self, index):
        sendWhosOnline(index)

    def handleRequestEditMap(self, index):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            print "hacking attempt"
            return

        sendEditMap(index)

    def handleRequestEditItem(self, index):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            print "hacking attempt"
            return

        sendItemEditor(index)

    def handleSaveItem(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_CREATOR:
            print "hacking attempt"
            return

        itemNum = jsonData[0]['itemnum']

        if itemNum < 0 or itemNum > MAX_ITEMS:
            print 'hacking attempt'
            return

        # update item
        Item[itemNum].name = jsonData[0]['itemname']
        Item[itemNum].pic = jsonData[0]['itempic']
        Item[itemNum].type = jsonData[0]['itemtype']
        Item[itemNum].data1 = jsonData[0]['itemdata1']
        Item[itemNum].data2 = jsonData[0]['itemdata2']
        Item[itemNum].data3 = jsonData[0]['itemdata3']

        # save item
        sendUpdateItemToAll(itemNum)
        # saveItem
        g.connectionLogger.info(getPlayerName(index) + ' saved item #' + str(itemNum) + '.')

    def handleSetAccess(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_CREATOR:
            print "hacking attempt"
            return

        plrName = jsonData[0]['name']
        access = jsonData[0]['access']

        plrIndex = findPlayer(plrName)

        # check for invalid access level
        if access >= 1 or access <= 4:
            if plrIndex is not None:

                if getPlayerAccess(plrIndex) == getPlayerAccess(index):
                    playerMsg(index, 'Invalid access level.', textColor.RED)
                    return

                if getPlayerAccess(plrIndex) <= 0:
                    # globalMsg
                    print "todo"

                setPlayerAccess(plrIndex, access)
                sendPlayerData(plrIndex)
                g.connectionLogger.info(getPlayerName(index) + ' has modified ' + getPlayerName(plrIndex) + 's access.')
            else:
                playerMsg(index, 'Player is not online.', textColor.WHITE)
        else:
            playerMsg(index, 'Invalid access level.', textColor.RED)

    def handleGiveItem(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            print "hacking attempt"
            return

        plrName = jsonData[0]['name']
        itemNum = jsonData[0]['itemnum']

        plrIndex = findPlayer(plrName)

        giveItem(plrIndex, itemNum, 1)


    def handleQuit(self, index):
        closeConnection(index)
