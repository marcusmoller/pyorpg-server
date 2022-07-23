import random

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

        elif packetType == ClientPackets.CEmoteMsg:
            self.handleEmoteMsg(index, jsonData)

        elif packetType == ClientPackets.CBroadcastMsg:
            self.handleBroadcastMsg(index, jsonData)

        elif packetType == ClientPackets.CGlobalMsg:
            self.handleGlobalMsg(index, jsonData)

        elif packetType == ClientPackets.CAdminMsg:
            self.handleAdminMsg(index, jsonData)

        elif packetType == ClientPackets.CPlayerMsg:
            self.handlePlayerMsg(index, jsonData)

        elif packetType == ClientPackets.CPlayerMove:
            self.handlePlayerMove(index, jsonData)

        elif packetType == ClientPackets.CPlayerDir:
            self.handlePlayerDir(index, jsonData)

        elif packetType == ClientPackets.CUseItem:
            self.handleUseItem(index, jsonData)

        elif packetType == ClientPackets.CCast:
            self.handleCastSpell(index, jsonData)

        elif packetType == ClientPackets.CTarget:
            self.handleTarget(index, jsonData)

        elif packetType == ClientPackets.CAttack:
            self.handleAttack(index)

        elif packetType == ClientPackets.CSpells:
            self.handleSpells(index)

        elif packetType == ClientPackets.CPlayerInfoRequest:
            self.handlePlayerInfoRequest(index, jsonData)

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

        elif packetType == ClientPackets.CMapGetItem:
            self.handleMapGetItem(index)

        elif packetType == ClientPackets.CMapReport:
            self.handleMapReport(index)

        elif packetType == ClientPackets.CMapRespawn:
            self.handleMapRespawn(index)

        elif packetType == ClientPackets.CWhosOnline:
            self.handleWhosOnline(index)

        elif packetType == ClientPackets.CRequestEditMap:
            self.handleRequestEditMap(index)

        elif packetType == ClientPackets.CRequestEditItem:
            self.handleRequestEditItem(index)

        elif packetType == ClientPackets.CSaveItem:
            self.handleSaveItem(index, jsonData)

        elif packetType == ClientPackets.CRequestEditSpell:
            self.handleRequestEditSpell(index)

        elif packetType == ClientPackets.CEditSpell:
            self.handleEditSpell(index, jsonData)

        elif packetType == ClientPackets.CSaveSpell:
            self.handleSaveSpell(index, jsonData)

        elif packetType == ClientPackets.CRequestEditNpc:
            self.handleRequestEditNpc(index)

        elif packetType == ClientPackets.CEditNpc:
            self.handleEditNpc(index, jsonData)

        elif packetType == ClientPackets.CSaveNpc:
            self.handleSaveNpc(index, jsonData)

        elif packetType == ClientPackets.CSetAccess:
            self.handleSetAccess(index, jsonData)

        elif packetType == ClientPackets.CGiveItem:
            self.handleGiveItem(index, jsonData)

        elif packetType == ClientPackets.CQuit:
            self.handleQuit(index)

        else:
            # Packet is unknown - hacking attempt
            hackingAttempt(index, 'Packet Modification')

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
                    print("hacking attempt")
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
                    alertMsg(index, "The acount name or password is too short!")
                    return
                
                #Not necessary
                '''if not accountExists(plrName):
                    # alert msg
                    return'''

                if not passwordOK(plrName, plrPassword):
                    alertMsg(index, "Wrong account name or password!")
                    return

                if isMultiAccounts(plrName):
                    alertMsg(index, "That account is already logged in!")
                    g.conn.closeConnection(index)

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
                alertMsg(index, 'Character name must be at least three characters in length.')
                return

            #todo: check for certain letters


            if charNum < 0 or charNum > MAX_CHARS:
                alertMsg(index, 'Invalid CharNum')
                return

            #todo: check sex

            if Class < 0 or Class > g.maxClasses:
                alertMsg(index, 'Invalid Class')
                return

            # check if a character already exists in slot
            if charExist(index, charNum):
                alertMsg(index, 'Character already exists')
                return

            # check if name is in use
            if findChar(name):
                alertMsg(index, 'Sorry, but that name is in use!')
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
                hackingAttempt(index, 'Invalid CharNum')
                return

            # make sure character exists
            if charExist(index, charNum):
                TempPlayer[index].charNum = charNum
                joinGame(index)

                g.connectionLogger.info("Has begun playing")

    ''' say msg '''
    def handleSayMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        mapMsg(getPlayerMap(index), getPlayerName(index) + ': ' + msg, sayColor)

    def handleEmoteMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        mapMsg(getPlayerMap(index), getPlayerName(index) + ' ' + msg, emoteColor)

    def handleBroadcastMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]

        # prevent hacking
        # check size
        string = getPlayerName(index) + ': ' + msg
        globalMsg(string, broadcastColor)

    def handleGlobalMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        if getPlayerAccess(index) > 0:
            string = '(global) ' + getPlayerName(index) +': ' + msg
            globalMsg(string, globalColor)

    def handleAdminMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        if getPlayerAccess(index) > 0:
            string = '(admin ' + getPlayerName(index) +') ' + msg
            globalMsg(string, adminColor)

    ''' Player message '''
    def handlePlayerMsg(self, index, jsonData):
        msg = jsonData[0]["msg"]
        msgTo = findPlayer(jsonData[0]["msgto"])

        # check if they are talking to themselves
        if msgTo != index:
            if msgTo is not None:
                playerMsg(msgTo, getPlayerName(index) + ' tells you "' + getPlayerName(msgTo) + ', ' + msg + '"', tellColor)
                playerMsg(index, 'You tell ' + getPlayerName(msgTo) + ', "' + msg + '"', tellColor)

            else:
                playerMsg(index, 'Player is not online.', textColor.WHITE)

        else:
            playerMsg(index, 'You cannot message yourself.', textColor.BRIGHT_RED)

    ''' Player movement '''
    def handlePlayerMove(self, index, jsonData):
        if TempPlayer[index].gettingMap:
            return

        direction = jsonData[0]["direction"]
        movement = jsonData[0]["moving"]

        # prevent hacking
        if direction < DIR_UP or direction > DIR_RIGHT:
            hackingAttempt(index, 'Invalid Direction')

        # prevent hacking
        if movement < 1 or movement > 2:
            hackingAttempt(index, 'Invalid Movement')

        # prevent player from moving if they have casted a spell
        if TempPlayer[index].castedSpell:
            # check if they have already casted a spell and if so we cant let them move
            tickCount = time.time() * 1000
            if tickCount > TempPlayer[index].attackTimer + 1000:
                TempPlayer[index].castedSpell = False

            else:
                sendPlayerXY(index)
                return

        playerMove(index, direction, movement)

    ''' Player direction '''
    def handlePlayerDir(self, index, jsonData):
        direction = jsonData[0]["direction"]
        setPlayerDir(index, direction)
        sendPlayerDir(index)

    def handleUseItem(self, index, jsonData):
        invNum = jsonData[0]['invnum']
        charNum = TempPlayer[index].charNum

        # prevent cheating
        if invNum < 0 or invNum > MAX_ITEMS:
            hackingAttempt(index, 'Invalid invNum')
            return

        if charNum < 0 or charNum > MAX_CHARS:
            hackingAttempt(index, 'Invalid charNum')
            return

        if getPlayerInvItemNum(index, invNum) >= 0 and getPlayerInvItemNum(index, invNum) <= MAX_ITEMS:
            n = Item[getPlayerInvItemNum(index, invNum)].data2

            # find out what item it is
            itemType = Item[getPlayerInvItemNum(index, invNum)].type

            if itemType == ITEM_TYPE_HELMET:
                if invNum != getPlayerEquipmentSlot(index, Equipment.helmet):
                    # todo: check if required stats have been met
                    setPlayerEquipmentSlot(index, invNum, Equipment.helmet)
                else:
                    setPlayerEquipmentSlot(index, None, Equipment.helmet)

                sendWornEquipment(index)

            elif itemType == ITEM_TYPE_ARMOR:
                if invNum != getPlayerEquipmentSlot(index, Equipment.armor):
                    # todo: check if required stats have been met
                    setPlayerEquipmentSlot(index, invNum, Equipment.armor)
                else:
                    setPlayerEquipmentSlot(index, None, Equipment.armor)

                sendWornEquipment(index)

            elif itemType == ITEM_TYPE_WEAPON:
                if invNum != getPlayerEquipmentSlot(index, Equipment.weapon):
                    # todo: check if required stats have been met
                    setPlayerEquipmentSlot(index, invNum, Equipment.weapon)
                else:
                    setPlayerEquipmentSlot(index, None, Equipment.weapon)

                sendWornEquipment(index)

            elif itemType == ITEM_TYPE_SHIELD:
                if invNum != getPlayerEquipmentSlot(index, Equipment.shield):
                    # todo: check if required stats have been met
                    setPlayerEquipmentSlot(index, invNum, Equipment.shield)
                else:
                    setPlayerEquipmentSlot(index, None, Equipment.shield)

                sendWornEquipment(index)

            elif itemType == ITEM_TYPE_SPELL:
                # spell num
                spellNum = Item[getPlayerInvItemNum(index, invNum)].data1

                if spellNum != None:
                    # make sure they are the right class
                    if int(1 if Spell[spellNum].reqClass is None else Spell[spellNum].reqClass) - 1 == getPlayerClass(index) or Spell[n].reqClass is None:
                        # make sure they are the right level
                        levelReq = Spell[spellNum].reqLevel

                        if levelReq <= getPlayerLevel(index):
                            i = findOpenSpellSlot(index)

                            if i is not None:
                                if not hasSpell(index, spellNum):
                                    setPlayerSpell(index, i, spellNum)
                                    takeItem(index, getPlayerInvItemNum(index, invNum), 0)
                                    playerMsg(index, 'You study the spell carefully...', textColor.YELLOW)
                                    playerMsg(index, 'You have learned a new spell!', textColor.WHITE)

                                else:
                                    playerMsg(index, 'You have already learned this spell!', textColor.BRIGHT_RED)

                            else:
                                playerMsg(index, 'You have learned all that you can learn!', textColor.BRIGHT_RED)

                        else:
                            playerMsg(index, 'You must be level ' + str(levelReq) + ' to learn this spell.', textColor.WHITE)

                    else:
                        playerMsg(index, 'This spell can only be learned by a '+ getClassName(Spell[spellNum].reqClass) + '.', textColor.WHITE)

                else:
                    playerMsg(index, 'An error occured with the spell. Please inform an admin!', textColor.WHITE)

            # todo: potions, keys

    def handleCastSpell(self, index, jsonData):
        spellSlot = jsonData[0]['spellslot']
        castSpell(index, spellSlot)

    def handleTarget(self, index, jsonData):
        x = jsonData[0]['x']
        y = jsonData[0]['y']

        if x < 0 or x > MAX_MAPX or y < 0 or y > MAX_MAPY:
            return

        # check for player
        for i in range(len(g.playersOnline)):
            if getPlayerMap(index) == getPlayerMap(g.playersOnline[i]):
                if getPlayerX(g.playersOnline[i]) == x and getPlayerY(g.playersOnline[i]) == y:
                    # consider the player
                    if g.playersOnline[i] != index:

                        if getPlayerLevel(g.playersOnline[i]) >= getPlayerLevel(index) + 5:
                            playerMsg(index, 'You wouldn\'t stand a chance.', textColor.BRIGHT_RED)

                        elif getPlayerLevel(g.playersOnline[i]) > getPlayerLevel(index):
                                playerMsg(index, 'This one seems to have an advantage over you.', textColor.YELLOW)

                        elif getPlayerLevel(g.playersOnline[i]) == getPlayerLevel(index):
                                playerMsg(index, 'This would be an even fight.', textColor.WHITE)

                        elif getPlayerLevel(g.playersOnline[i]) + 5 <= getPlayerLevel(index):
                                playerMsg(index, 'You could slaughter that player.', textColor.BRIGHT_BLUE)

                        elif getPlayerLevel(g.playersOnline[i]) < getPlayerLevel(index):
                                playerMsg(index, 'You would have an advantage over that player.', textColor.YELLOW)



                        # change the target
                        TempPlayer[index].target = g.playersOnline[i]
                        TempPlayer[index].targetType = TARGET_TYPE_PLAYER
                        playerMsg(index, 'Your target is now ' + getPlayerName(g.playersOnline[i]) + '.', textColor.YELLOW)
                        return

        # check for npc
        for i in range(MAX_MAP_NPCS):
            if mapNPC[getPlayerMap(index)][i].num is not None:
                if mapNPC[getPlayerMap(index)][i].x == x and mapNPC[getPlayerMap(index)][i].y == y:
                    # change the target
                    TempPlayer[index].target = i
                    TempPlayer[index].targetType = TARGET_TYPE_NPC
                    playerMsg(index, 'Your target is now a ' + NPC[mapNPC[getPlayerMap(index)][i].num].name + '.', textColor.YELLOW)
                    return



    def handleAttack(self, index):
        # try to attack a player
        for i in range(g.totalPlayersOnline):
            tempIndex = g.playersOnline[i]

            # make sure we dont attack ourselves
            if tempIndex != index:
                # can we attack the player?
                if canAttackPlayer(index, tempIndex):
                    # check if player can block the hit
                    if not canPlayerBlockHit(tempIndex):

                        # get the damage we can do
                        if not canPlayerCriticalHit(index):
                            # normal hit
                            damage = getPlayerDamage(index) - getPlayerProtection(tempIndex)

                        else:
                            # critical hit so add bonus
                            n = getPlayerDamage(index)
                            damage = n + random.randint(1, (n // 2)) + 1 - getPlayerProtection(tempIndex)

                            playerMsg(index, 'You feel a surge of energy upon swinging!', textColor.BRIGHT_CYAN)
                            playerMsg(tempIndex, getPlayerName(index) + ' swings with enormous might!', textColor.BRIGHT_CYAN)

                        attackPlayer(index, tempIndex, damage)

                    else:
                        # player has blocked the hit
                        playerMsg(index, getPlayerName(tempIndex) + '\'s ' + Item[getPlayerInvItemNum(tempIndex, getPlayerEquipmentSlot(tempIndex, Equipment.shield))].name + ' has blocked your hit!', textColor.BRIGHT_CYAN)
                        playerMsg(tempIndex, 'Your ' + Item[getPlayerInvItemNum(tempIndex, getPlayerEquipmentSlot(tempIndex, Equipment.shield))].name + ' has blocked ' + getPlayerName(index) + '\'s hit!', textColor.BRIGHT_CYAN)

        # todo: handle attack npc
        for i in range(MAX_MAP_NPCS):
            if canAttackNpc(index, i):
                # get the damage we can do
                if not canPlayerCriticalHit(index):
                    damage = getPlayerDamage(index) - (NPC[mapNPC[getPlayerMap(index)][i].num].stat[Stats.defense] // 2)

                else:
                    n = getPlayerDamage(index)
                    damage = n + random.randint(0, n // 2) + 1 - (NPC[mapNPC[getPlayerMap(index)][i].num].stat[Stats.defense] // 2)

                    playerMsg(index, 'You feel a surge of energy upon swinging!', textColor.BRIGHT_CYAN)

                if damage > 0:
                    attackNpc(index, i, damage)
                    
                else:
                    playerMsg(index, 'Your attack does nothing.', textColor.BRIGHT_RED)

    def handleSpells(self, index):
        sendPlayerSpells(index)

    def handlePlayerInfoRequest(self, index, jsonData):
        name = jsonData[0]['name']

        i = findPlayer(name)

        if i != None:
            playerMsg(index, 'Account: ' + Player[i].Login + ', Name: ' + getPlayerName(i), textColor.BRIGHT_GREEN)

            if getPlayerAccess(index) > ADMIN_MONITOR:
                playerMsg(index, '-=- Stats for ' + getPlayerName(i) + ' -=-', textColor.BRIGHT_GREEN)
                playerMsg(index, 'Level: ' + str(getPlayerLevel(i)) + ' EXP: ' + str(getPlayerExp(i)) + '/' + str(getPlayerNextLevel(i)), textColor.BRIGHT_GREEN)
                playerMsg(index, 'HP: ' + str(getPlayerVital(i, Vitals.hp)) + '/' + str(getPlayerMaxVital(i, Vitals.hp)) + ' MP: ' + str(getPlayerVital(i, Vitals.mp)) + '/' + str(getPlayerMaxVital(i, Vitals.mp)) + ' SP: ' + str(getPlayerVital(i, Vitals.sp)) + '/' + str(getPlayerMaxVital(i, Vitals.sp)), textColor.BRIGHT_GREEN)
                playerMsg(index, 'Strength: ' + str(getPlayerStat(i, Stats.strength)) + ' Defense: ' + str(getPlayerStat(i, Stats.defense)) + ' Magic: ' + str(getPlayerStat(i, Stats.magic)) + ' Speed: ' + str(getPlayerStat(i, Stats.speed)), textColor.BRIGHT_GREEN)

                n = (getPlayerStat(i, Stats.strength) // 2) + (getPlayerLevel(i) // 2)
                k = (getPlayerStat(i, Stats.defense) // 2) + (getPlayerLevel(i) // 2)

                if n > 100:
                    n = 100

                if k > 100:
                    k = 100

                playerMsg(index, 'Critical Hit Chance: ' + str(n) + '%, Block Chance: ' + str(k) + '%', textColor.BRIGHT_GREEN)
        else:
            playerMsg(index, 'Player is not online.', textColor.WHITE)


    def handleWarpMeTo(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
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
            hackingAttempt(index, 'Admin Cloning')
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
            hackingAttempt(index, 'Admin Cloning')
            return

        mapNum = jsonData[0]['map']

        if mapNum < 0 or mapNum > MAX_MAPS:
            hackingAttempt(index, 'Invalid MapNum')
            return

        playerWarp(index, mapNum, getPlayerX(index), getPlayerY(index))
        playerMsg(index, 'You have been warped to map #' + str(mapNum), textColor.BRIGHT_BLUE)
        g.connectionLogger.info(getPlayerName(index) + ' warped to map #' + str(mapNum))

    def handleSetSprite(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        n = jsonData[0]["sprite"]

        setPlayerSprite(index, n)
        sendPlayerData(index)

    def handleRequestNewMap(self, index, jsonData):
        direction = jsonData[0]["direction"]

        if direction < DIR_UP or direction > DIR_RIGHT:
            print("hacking attempt")
            return

        playerMove(index, direction, 1)

    def handleMapData(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
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
                Map[mapNum].tile[x][y].layer1 = jsonData[tile_i][0]["layer1"]
                Map[mapNum].tile[x][y].layer2 = jsonData[tile_i][0]["layer2"]
                Map[mapNum].tile[x][y].layer3 = jsonData[tile_i][0]["layer3"]
                Map[mapNum].tile[x][y].mask   = jsonData[tile_i][0]["mask"]
                Map[mapNum].tile[x][y].anim   = jsonData[tile_i][0]["animation"]
                Map[mapNum].tile[x][y].fringe = jsonData[tile_i][0]["fringe"]
                Map[mapNum].tile[x][y].type   = jsonData[tile_i][0]["type"]
                Map[mapNum].tile[x][y].data1  = jsonData[tile_i][0]["data1"]
                Map[mapNum].tile[x][y].data2  = jsonData[tile_i][0]["data2"]
                Map[mapNum].tile[x][y].data3  = jsonData[tile_i][0]["data3"]

                tile_i += 1

        for i in range(MAX_MAP_NPCS):
            Map[mapNum].npc[i] = jsonData[tile_i][0]['npcnum']
            clearMapNpc(i, mapNum)

            tile_i += 1

        sendMapNpcsToMap(mapNum)
        spawnMapNpcs(mapNum)

        # clear map items
        for i in range(MAX_MAP_ITEMS):            
            spawnItemSlot(i, None, None, None, getPlayerMap(index), mapItem[getPlayerMap(index)][i].x, mapItem[getPlayerMap(index)][i].y)
            clearMapItem(i, getPlayerMap(index))

        # respawn items
        spawnMapItems(getPlayerMap(index))

        # save map
        saveMap(mapNum)
        mapCacheCreate(mapNum)

        # refresh map for everyone online
        for i in range(g.totalPlayersOnline):
            index = g.playersOnline[i]

            if isPlaying(index):
                if getPlayerMap(index) == mapNum:
                    playerWarp(index, mapNum, getPlayerX(index), getPlayerY(index))


    def handleNeedMap(self, index, jsonData):
        g.serverLogger.debug("handleNeedMap()")
        answer = jsonData[0]["answer"]

        if answer == 1:
            # needs new revision
            sendMap(index, getPlayerMap(index))

        sendMapItemsTo(index, getPlayerMap(index))
        sendMapNpcsTo(index, getPlayerMap(index))
        sendJoinMap(index)
        TempPlayer[index].gettingMap = False

        sendMapDone(index)

        # todo: senddoordata

    def handleMapGetItem(self, index):
        playerMapGetItem(index)

    def handleMapReport(self, index):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        msg = 'Free Maps: '
        tMapStart = 1
        tMapEnd = 1

        for i in range(MAX_MAPS):
            if len(Map[i].name) == 0:
                tMapEnd += 1

            else:
                if tMapEnd - tMapStart > 0:
                    msg += str(tMapStart) + '-' + str(tMapEnd-1) + ', '

                tMapStart = i + 1
                tMapEnd = i + 1

        msg += str(tMapStart) + '-' + str(tMapEnd-1) + ', '
        msg = msg[:-2] + '.'

        playerMsg(index, msg, textColor.BROWN)

    def handleMapRespawn(self, index):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        # clear it all
        for i in range(MAX_MAP_ITEMS):
            spawnItemSlot(i, None, None, None, getPlayerMap(index), mapItem[getPlayerMap(index)][i].x, mapItem[getPlayerMap(index)][i].y)
            clearMapItem(i, getPlayerMap(index))

        # respawn
        spawnMapItems(getPlayerMap(index))

        # respawn npcs
        for i in range(MAX_MAP_NPCS):
            spawnNpc(i, getPlayerMap(index))

        playerMsg(index, 'Map respawned.', textColor.BLUE)
        g.connectionLogger.info(getPlayerName(index) + ' has respawned map #' + str(getPlayerMap(index)) + '.')


    def handleMapDropItem(self, index, jsonData):
        invNum = jsonData[0]['invnum']
        amount = jsonData[0]['amount']

        # prevent hacking
        if invNum < 1 or invNum > MAX_INV:
            return

        if amount > getPlayerInvItemValue(index, invNum):
            return

        if Item[getPlayerInvItemNum(index, invNum)].type == ITEM_TYPE_CURRENCY:
            # check if money and if so, make sure it wont drop to value 0
            if amoun <= 0:
                # hacking attemt
                takeItem(index, getPlayerInvItemNum(index, invNum), 0)

        playerMapDropItem(index, invNum, amount)

    def handleWhosOnline(self, index):
        sendWhosOnline(index)

    def handleRequestEditMap(self, index):
        if getPlayerAccess(index) < ADMIN_MAPPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        sendEditMap(index)

    def handleRequestEditItem(self, index):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        sendItemEditor(index)

    def handleSaveItem(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_CREATOR:
            hackingAttempt(index, 'Admin Cloning')
            return

        itemNum = int(jsonData[0]['itemnum'])

        if itemNum < 0 or itemNum > MAX_ITEMS:
            hackingAttempt(index, 'Invalid ItemNum')
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
        saveItem(itemNum)
        g.connectionLogger.info(getPlayerName(index) + ' saved item #' + str(itemNum) + '.')
        playerMsg(index, Item[itemNum].name + ' was saved as item #' + str(itemNum), textColor.BRIGHT_BLUE)

    def handleRequestEditSpell(self, index):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')

        sendSpellEditor(index)

    def handleEditSpell(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        spellNum = jsonData[0]['spellnum']

        # prevent hacking
        if spellNum < 0 or spellNum > MAX_SPELLS:
            hackingAttempt(index, 'Invalid Spell Index')

        g.connectionLogger.info(getPlayerName(index) + ' editing spell #' + str(spellNum) + '.')
        sendEditSpellTo(index, spellNum)

    def handleSaveSpell(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')

        # spell num
        spellNum = jsonData[0]['spellnum']

        # prevent hacking
        if spellNum is None or spellNum > MAX_SPELLS:
            hackingAttempt(index, 'Invalid Spell Index')

        # update spell
        Spell[spellNum].name = jsonData[0]['spellname']
        Spell[spellNum].pic = jsonData[0]['spellpic']
        Spell[spellNum].type = jsonData[0]['spelltype']

        Spell[spellNum].reqMp = jsonData[0]['mpreq']
        Spell[spellNum].reqClass = jsonData[0]['classreq']
        Spell[spellNum].reqLevel = jsonData[0]['levelreq']

        Spell[spellNum].data1 = jsonData[0]['data1']
        Spell[spellNum].data2 = jsonData[0]['data2']
        Spell[spellNum].data3 = jsonData[0]['data3']

        # save
        sendUpdateSpellToAll(spellNum)
        saveSpell(spellNum)
        g.serverLogger.info(getPlayerName(index) + ' saved spell #' + str(spellNum) + '.')


    def handleRequestEditNpc(self, index):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        sendNpcEditor(index)

    def handleEditNpc(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        npcNum = jsonData[0]['npcnum']

        # prevent hacking
        if npcNum < 0 or npcNum > MAX_NPCS:
            hackingAttempt(index, 'Invalid NPC Index')

        g.connectionLogger.info(getPlayerName(index) + ' editing NPC #' + str(npcNum) + '.')
        sendEditNpcTo(index, npcNum)

    def handleSaveNpc(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        npcNum = jsonData[0]['npcnum']

        if npcNum < 0 or npcNum > MAX_NPCS:
            return

        # update npc
        NPC[npcNum].name = jsonData[0]['name']
        NPC[npcNum].attackSay = jsonData[0]['attacksay']
        NPC[npcNum].sprite = jsonData[0]['sprite']
        NPC[npcNum].spawnSecs = jsonData[0]['spawnsec']
        NPC[npcNum].behaviour = jsonData[0]['behavior']
        NPC[npcNum].range = jsonData[0]['range']

        NPC[npcNum].dropChance = jsonData[0]['dropchance']
        NPC[npcNum].dropItem = jsonData[0]['dropitem']
        NPC[npcNum].dropItemValue = jsonData[0]['dropitemval']

        NPC[npcNum].stat[Stats.strength] = jsonData[0]['strength']
        NPC[npcNum].stat[Stats.defense] = jsonData[0]['defense']
        NPC[npcNum].stat[Stats.magic] = jsonData[0]['magic']
        NPC[npcNum].stat[Stats.speed] = jsonData[0]['speed']

        # save it
        sendUpdateNpcToAll(npcNum)
        saveNpc(npcNum)
        g.connectionLogger.info(getPlayerName(index) + ' saved NPC #' + str(npcNum) + '.')
        playerMsg(index, NPC[npcNum].name + ' was saved as NPC #' + str(npcNum), textColor.BRIGHT_BLUE)

    def handleSetAccess(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_CREATOR:
            hackingAttempt(index, 'Admin Cloning')
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
                    globalMsg(getPlayerName(index) + ' has been blessed with administrative access.', textColor.BRIGHT_BLUE)

                setPlayerAccess(plrIndex, access)
                sendPlayerData(plrIndex)
                g.connectionLogger.info(getPlayerName(index) + ' has modified ' + getPlayerName(plrIndex) + 's access.')
            else:
                playerMsg(index, 'Player is not online.', textColor.WHITE)
        else:
            playerMsg(index, 'Invalid access level.', textColor.RED)

    def handleGiveItem(self, index, jsonData):
        if getPlayerAccess(index) < ADMIN_DEVELOPER:
            hackingAttempt(index, 'Admin Cloning')
            return

        plrName = jsonData[0]['name']
        itemNum = jsonData[0]['itemnum']

        plrIndex = findPlayer(plrName)

        giveItem(plrIndex, itemNum, 1)


    def handleSearch(self, index, jsonData):
        x = jsonData[0]['x']
        y = jsonData[0]['y']

        if x < 0 or x > MAX_MAPX or y < 0 or y > MAX_MAPY:
            return

        for i in range(g.totalPlayersOnline):
            if getPlayerMap(index) == getPlayerMap(g.playersOnline[i]):
                if getPlayerX(g.playersOnline[i]) == x:
                    if getPlayerY(g.playersOnline[i]) == y:

                        # consider the player
                        if g.playersOnline[i] != index:
                            if getPlayerLevel(playersOnline[i]) >= getPlayerLevel(index) + 5:
                                playerMsg(index, "You wouldn't stand a chance.", textColor.BRIGHT_RED)

                            elif getPlayerLevel(playersOnline[i]) > getPlayerLevel(index):
                                playerMsg(index, "This one seems to have an advantage over you.", textColor.YELLOW)

                            elif getPlayerLevel(playersOnline[i]) == getPlayerLevel(index):
                                playerMsg(index, "This would be an even fight.", textColor.WHITE)

                            elif getPlayerLevel(playersOnline[i]) + 5 <= getPlayerLevel(index):
                                playerMsg(index, "You could slaughter that player.", textColor.BRIGHT_BLUE)

                            elif getPlayerLevel(playersOnline[i]) < getPlayerLevel(index):
                                playerMsg(index, "You would have an advantage over that player.", textColor.YELLOW)

                    # todo: change target

        for i in range(MAX_MAP_ITEMS):
            if mapItem[getPlayerMap(index)][i].num != None:
                if mapItem[getPlayerMap(index)][i].x == x and mapItem[getPlayerMap(index)][i].y == y:
                    playerMsg(index, 'You see a ' + Item[mapItem[getPlayerMap(index)][i].num].name + '.', textColor.YELLOW)




    def handleQuit(self, index):
        closeConnection(index)
