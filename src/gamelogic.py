import time
import json
import random

from database import *
from objects import *
from constants import *
from packettypes import *
from utils import *

import globalvars as g

def canAttackPlayer(attacker, victim):
    # check attack timer
    if time.time() < TempPlayer[attacker].attackTimer + 1:
        return False

    # check for subscript out of range
    if not isPlaying(victim):
        return False

    # make sure they are on the same map
    if not getPlayerMap(attacker) == getPlayerMap(victim):
        return False

    # make sure we dont attack the player if they are switching maps
    if TempPlayer[victim].gettingMap == True:
        return False

    # check if at same coordinates

    attackDir = getPlayerDir(attacker)

    if attackDir == DIR_UP:
        if not ((getPlayerY(victim) + 1 == getPlayerY(attacker)) and (getPlayerX(victim) == getPlayerX(attacker))):
            return False
    elif attackDir == DIR_DOWN:
        if not ((getPlayerY(victim) - 1 == getPlayerY(attacker)) and (getPlayerX(victim) == getPlayerX(attacker))):
            return False
    elif attackDir == DIR_LEFT:
        if not ((getPlayerY(victim) == getPlayerY(attacker)) and (getPlayerX(victim) + 1 == getPlayerX(attacker))):
            return False
    elif attackDir == DIR_RIGHT:
        if not ((getPlayerY(victim) == getPlayerY(attacker)) and (getPlayerX(victim) - 1 == getPlayerX(attacker))):
            return False

    # check if map is attackable
    # todo

    # make sure they have more than 0 hp
    if getPlayerVital(victim, Vitals.hp) <= 0:
        return False

    # check to make sure they dont have access
    # todo

    # check to make sure the victim isnt an admin
    # todo

    # make sure attacker is high enough level
    # todo

    # make sure victim is high enough level
    # todo

    return True

def attackPlayer(attacker, victim, damage):
    # check for subscript out of range
    if isPlaying(attacker) == False or isPlaying(victim) == False or damage < 0:
        return

    # check weapon
    weaponNum = None
    if getPlayerEquipmentSlot(attacker, Equipment.weapon) != None:
        weaponNum = getPlayerInvItemNum(attacker, getPlayerEquipmentSlot(attacker, Equipment.weapon))

    # send packet to map so they can see person attacking
    packet = json.dumps([{"packet": ServerPackets.SAttack, "attacker": attacker}])
    g.conn.sendDataToMapBut(getPlayerMap(attacker), attacker, packet)

    # reduce durability on victims equipment
    damageEquipment(victim, Equipment.armor)
    damageEquipment(victim, Equipment.helmet)

    if damage >= getPlayerVital(victim, Vitals.hp):
        # player dies on hit
        if weaponNum is None:
            # no weapon
            playerMsg(attacker, 'You hit ' + getPlayerName(victim) + ' for ' + str(damage) + ' hit points.', textColor.WHITE)
            playerMsg(victim, getPlayerName(attacker) + ' hit you for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

        else:
            # a weapon is equipped
            playerMsg(attacker, 'You hit ' + getPlayerName(victim) + ' with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points.', textColor.WHITE)
            playerMsg(victim, getPlayerName(attacker) + ' hit you with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

        # player is dead
        globalMsg(getPlayerName(victim) + ' has been killed by ' + getPlayerName(attacker), textColor.BRIGHT_RED)

        # calculate exp
        exp = getPlayerExp(victim) // 10

        if exp < 0:
            exp = 0

        if exp == 0:
            playerMsg(victim, 'You lost no experience points.', textColor.BRIGHT_RED)
            playerMsg(attacker, 'You received no experience points from that weak insignificant player.', textColor.BRIGHT_BLUE)

        else:
            setPlayerExp(victim, getPlayerExp(victim) - exp)
            playerMsg(victim, 'You lost ' + exp + 'experience points.', textColor.BRIGHT_RED)

            setPlayerExp(attacker, getPlayerExp(attacker) + exp)
            playerMsg(attacker, 'You gained ' + exp + 'experience points for killing ' + getPlayerName(victim) + '.', textColor.BRIGHT_RED)

        # check for level up
        checkPlayerLevelUp(attacker)

        # todo: check if target is player who died, if so set target to 0

        onDeath(victim)

    else:
        # player doesnt die on hit, just do damage
        setPlayerVital(victim, Vitals.hp, getPlayerVital(victim, Vitals.hp) - damage)
        sendVital(victim, Vitals.hp)

        if weaponNum is None:
            # no weapon
            playerMsg(attacker, 'You hit ' + getPlayerName(victim) + ' for ' + str(damage) + ' hit points.', textColor.WHITE)
            playerMsg(victim, getPlayerName(attacker) + ' hit you for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)
        else:
            # a weapon is equipped
            playerMsg(attacker, 'You hit ' + getPlayerName(victim) + ' with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points.', textColor.WHITE)
            playerMsg(victim, getPlayerName(attacker) + ' hit you with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

    # reduce durability of weapon
    damageEquipment(attacker, Equipment.weapon)

    # reset attack timer
    TempPlayer[attacker].attackTimer = time.time()


def playerMove(index, direction, movement):
    moved = False
    setPlayerDir(index, direction)

    if direction == DIR_UP:
        if getPlayerY(index) > 0:
            # TODO: Check if tilemap thing
            if Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)-1].type != TILE_TYPE_BLOCKED:
                setPlayerY(index, getPlayerY(index) - 1)

                packet = json.dumps([{"packet": ServerPackets.SPlayerMove, "index": index, "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index), "moving": movement}])
                g.conn.sendDataToAllBut(index, packet)
                moved = True
        else:
            if Map[getPlayerMap(index)].up > 0:
                playerWarp(index, Map[getPlayerMap(index)].up, getPlayerX(index), MAX_MAPY - 1)  # todo, dont use -1
                moved = True

    elif direction == DIR_DOWN:
        if getPlayerY(index) < MAX_MAPY-1:
            if Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)+1].type != TILE_TYPE_BLOCKED:
                setPlayerY(index, getPlayerY(index) + 1)

                packet = json.dumps([{"packet": ServerPackets.SPlayerMove, "index": index, "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index), "moving": movement}])
                g.conn.sendDataToAllBut(index, packet)
                moved = True

        else:
            if Map[getPlayerMap(index)].down > 0:
                playerWarp(index, Map[getPlayerMap(index)].down, getPlayerX(index), 0)
                moved = True

    elif direction == DIR_LEFT:
        if getPlayerX(index) > 0:
            if Map[getPlayerMap(index)].tile[getPlayerX(index)-1][getPlayerY(index)].type != TILE_TYPE_BLOCKED:
                setPlayerX(index, getPlayerX(index) - 1)

                packet = json.dumps([{"packet": ServerPackets.SPlayerMove, "index": index, "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index), "moving": movement}])
                g.conn.sendDataToAllBut(index, packet)
                moved = True

        else:
            if Map[getPlayerMap(index)].left > 0:
                playerWarp(index, Map[getPlayerMap(index)].left, MAX_MAPX-1, getPlayerY(index)) # todo, dont use -1
                moved = True

    elif direction == DIR_RIGHT:
        if getPlayerX(index) < MAX_MAPX-1:
            if Map[getPlayerMap(index)].tile[getPlayerX(index)+1][getPlayerY(index)].type != TILE_TYPE_BLOCKED:
                setPlayerX(index, getPlayerX(index) + 1)

                packet = json.dumps([{"packet": ServerPackets.SPlayerMove, "index": index, "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index), "moving": movement}])
                g.conn.sendDataToAllBut(index, packet)
                moved = True

        else:
            if Map[getPlayerMap(index)].right > 0:
                playerWarp(index, Map[getPlayerMap(index)].right, 0, getPlayerY(index)) # todo, dont use -1
                moved = True

    # check to see if the tile is a warp tile, and if so warp them
    if Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)].type == TILE_TYPE_WARP:
        mapNum = int(Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)].data1)
        x      = int(Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)].data2)
        y      = int(Map[getPlayerMap(index)].tile[getPlayerX(index)][getPlayerY(index)].data3)

        playerWarp(index, mapNum, x, y)
        moved = True

    if moved == False:
        # hacking attempt
        g.serverLogger.info("hacking attempt (playerMove)")


def getPlayerDamage(index):
    if not isPlaying(index) or index is None or index > g.highIndex:
        return 0

    plrDamage = (getPlayerStat(index, Stats.strength) // 2)

    if plrDamage <= 0:
        plrDamage = 1

    # check if player has a weapon equipped
    if getPlayerEquipmentSlot(index, Equipment.weapon) is not None:
        weaponSlot = getPlayerEquipmentSlot(index, Equipment.weapon)
        plrDamage += Item[getPlayerInvItemNum(index, weaponSlot)].data2

    return plrDamage


def getPlayerProtection(index):
    if not isPlaying(index) or index is None or index > g.highIndex:
        return 0

    armorSlot = getPlayerEquipmentSlot(index, Equipment.armor)
    helmetSlot = getPlayerEquipmentSlot(index, Equipment.helmet)

    plrProtection = (getPlayerStat(index, Stats.defense) // 5)

    if armorSlot != None:
        plrProtection += Item[getPlayerInvItemNum(index, armorSlot)].data2

    if helmetSlot != None:
        plrProtection += Item[getPlayerInvItemNum(index, helmetSlot)].data2

    return plrProtection


def canPlayerCriticalHit(index):
    # is a weapon equipped
    if getPlayerEquipmentSlot(index, Equipment.weapon) != None:
        n = random.randint(1, 2)

        if n == 1:
            # calculate critical hit chance
            i = (getPlayerStat(index, Stats.strength) // 2) + (getPlayerLevel(index) // 2)

            n = random.randint(1, 100)
            if n <= i:
                return True

    return False


def canPlayerBlockHit(index):
    # is a shield equipped
    if getPlayerEquipmentSlot(index, Equipment.shield) is not None:
        n = random.randint(1, 2)

        if n == 1:
            i = (getPlayerStat(index, Stats.defense) // 2) + (getPlayerLevel(index) // 2)

            n = random.randint(1, 100)
            if n <= i:
                return True

    return False


def playerWarp(index, mapNum, x, y):
    oldMap = getPlayerMap(index)

    if oldMap != mapNum:
        sendLeaveMap(index, oldMap)

    setPlayerMap(index, mapNum)
    setPlayerX(index, x)
    setPlayerY(index, y)

    playersOnMap[mapNum] = 1

    TempPlayer[index].gettingMap = 1

    packet = json.dumps([{"packet": ServerPackets.SCheckForMap, "mapnum": mapNum, "revision": Map[mapNum].revision}])
    g.conn.sendDataTo(index, packet)


    #packet = json.dumps([{"packet": ServerPackets.SPlayerMove, "index": index, "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index), "moving": 0}])
    #g.conn.sendDataToAllBut(index, packet)

def joinGame(index):
    TempPlayer[index].inGame = True

    g.totalPlayersOnline += 1
    updateHighIndex()

    if getPlayerAccess(index) <= ADMIN_MONITOR:
        globalMsg(getPlayerName(index) + " has joined!", joinLeftColor)
    else:
        globalMsg(getPlayerName(index) + " has joined!", textColor.WHITE)

    # send ok to client to start receiving game data
    packet = json.dumps([{"packet": ServerPackets.SLoginOK, "index": index}])
    g.conn.sendDataTo(index, packet)

    # send more goodies
    sendClasses(index)
    sendItems(index)
    # npc
    # shops
    # spells
    sendInventory(index)
    sendWornEquipment(index)

    for i in range(0, Vitals.vital_count):  # vital.vital_count -1
        sendVital(index, i)

    sendStats(index)

    # warp player to saved location
    playerWarp(index, getPlayerMap(index), getPlayerX(index), getPlayerY(index))

    # send welcome messages (todo)
    sendWelcome(index)

    # send that we're ingame
    packet = json.dumps([{"packet": ServerPackets.SInGame}])
    g.conn.sendDataTo(index, packet)


def leftGame(index):
    if TempPlayer[index].inGame:
        TempPlayer[index].inGame = False

        savePlayer(index)

        # send global msg that player left game
        if getPlayerAccess(index) <= ADMIN_MONITOR:
            globalMsg(getPlayerName(index) + ' has left ' + GAME_NAME + '!', joinLeftColor)
        else:
            globalMsg(getPlayerName(index) + ' has left ' + GAME_NAME + '!', textColor.WHITE)

        g.connectionLogger.info(getPlayerName(index) + ' has disconnected')
        sendLeftGame(index)

        g.totalPlayersOnline -= 1
        updateHighIndex()

    clearPlayer(index)


def findPlayer(name):
    for i in range(g.totalPlayersOnline):
        # dont check a name that is too small
        if len(getPlayerName(g.playersOnline[i])) >= len(name):
            if getPlayerName(g.playersOnline[i]).lower() == name.lower():
                return g.playersOnline[i]

    return None

def findOpenInvSlot(index, itemNum):
    if not isPlaying(index) or itemNum < 0 or itemNum > MAX_ITEMS:
        return

    if Item[itemNum].type == ITEM_TYPE_CURRENCY:
        # if the the item is currency, find and add to previous item
        for i in range(MAX_INV):
            if getPlayerInvItemNum(index, i) == itemNum:
                return i

    for i in range(0, MAX_INV):
        # try to find an open free slot
        if getPlayerInvItemNum(index, i) == None:
            return i

    return None

def hasItem(index, itemNum):
    if not isPlaying(index) or itemNum < 0 or itemNum > MAX_ITEMS:
        return

    for i in range(MAX_INV):
        if getPlayerInvItemNum(index, i):
            if Item[itemNum].type == ITEM_TYPE_CURRENCY:
                return getPlayerInvItemValue(index, i)

            else:
                return 1

def takeItem(index, itemNum, itemVal):
    if not isPlaying(index) or itemNum < 0 or itemNum > MAX_ITEMS:
        return

    takeItem = False

    for i in range(MAX_INV):
        # check if the player has the item
        if getPlayerInvItemNum(index, i) == itemNum:
            if Item[itemNum].type == ITEM_TYPE_CURRENCY:
                # are we trying to take away more than they have? if so, set to zero
                if itemVal >= getPlayerInvItemValue(index, i):
                    takeItem = True
                else:
                    setPlayerInvItemValue(index, i, getPlayerInvItemValue(index, i) - itemVal)
                    sendInventoryUpdate(index, i)

            else:
                # is it a weapon?
                if Item[getPlayerInvItemNum(index, i)].type == ITEM_TYPE_WEAPON:
                    if getPlayerEquipmentSlot(index, Equipment.weapon) != None:
                        if i == getPlayerEquipmentSlot(index, Equipment.weapon):
                            setPlayerEquipmentSlot(index, None, Equipment.weapon)
                            sendWornEquipment(index)
                            takeItem = True

                        else:
                            # check if the item we are taking isnt already equipped
                            if itemNum != getPlayerInvItemNum(index, getPlayerEquipmentSlot(index, Equipment.weapon)):
                                takeItem = True

                    else:
                        takeItem = True

                elif Item[getPlayerInvItemNum(index, i)].type == ITEM_TYPE_ARMOR:
                    if getPlayerEquipmentSlot(index, Equipment.armor) != None:
                        if i == getPlayerEquipmentSlot(index, Equipment.armor):
                            setPlayerEquipmentSlot(index, None, Equipment.armor)
                            sendWornEquipment(index)
                            takeItem = True

                        else:
                            # check if the item we are taking isnt already equipped
                            if itemNum != getPlayerInvItemNum(index, getPlayerEquipmentSlot(index, Equipment.armor)):
                                takeItem = True

                    else:
                        takeItem = True

                elif Item[getPlayerInvItemNum(index, i)].type == ITEM_TYPE_HELMET:
                    if getPlayerEquipmentSlot(index, Equipment.helmet) != None:
                        if i == getPlayerEquipmentSlot(index, Equipment.helmet):
                            setPlayerEquipmentSlot(index, None, Equipment.helmet)
                            sendWornEquipment(index)
                            takeItem = True

                        else:
                            # check if the item we are taking isnt already equipped
                            if itemNum != getPlayerInvItemNum(index, getPlayerEquipmentSlot(index, Equipment.helmet)):
                                takeItem = True

                    else:
                        takeItem = True

                elif Item[getPlayerInvItemNum(index, i)].type == ITEM_TYPE_SHIELD:
                    if getPlayerEquipmentSlot(index, Equipment.shield) != None:
                        if i == getPlayerEquipmentSlot(index, Equipment.shield):
                            setPlayerEquipmentSlot(index, None, Equipment.shield)
                            sendWornEquipment(index)
                            takeItem = True

                        else:
                            # check if the item we are taking isnt already equipped
                            if itemNum != getPlayerInvItemNum(index, getPlayerEquipmentSlot(index, Equipment.shield)):
                                takeItem = True

                    else:
                        takeItem = True

                # check if the item isnt equipable - if it isnt, take it away
                n = Item[getPlayerInvItemNum(index, i)].type
                if n != ITEM_TYPE_WEAPON or n!= ITEM_TYPE_ARMOR or n != ITEM_TYPE_HELMET or n != ITEM_TYPE_SHIELD:
                    takeItem = True

                if takeItem:
                    setPlayerInvItemNum(index, i, None)
                    setPlayerInvItemValue(index, i, 0)
                    setPlayerInvItemDur(index, i, 0)

                    # send inventory update
                    sendInventoryUpdate(index, i)


def giveItem(index, itemNum, itemVal):
    if not isPlaying(index) or itemNum < 0 or itemNum > MAX_ITEMS:
        return

    i = findOpenInvSlot(index, itemNum)

    # check if inventory is full
    if i is not None:
        setPlayerInvItemNum(index, i, itemNum)
        setPlayerInvItemValue(index, i, getPlayerInvItemValue(index, i) + itemVal)

        # if the item is equipment then add durability
        if Item[itemNum].type == ITEM_TYPE_ARMOR or Item[itemNum].type == ITEM_TYPE_WEAPON or Item[itemNum].type == ITEM_TYPE_HELMET or Item[itemNum].type == ITEM_TYPE_SHIELD:
            setPlayerInvItemDur(index, i, Item[itemNum].data1)

        sendInventoryUpdate(index, i)

    else:
        playerMsg(index, 'Your inventory is full.', textColor.BRIGHT_RED)


def checkPlayerLevelUp(index):
    # check if attacker got a level up
    if getPlayerExp(index) >= getPlayerNextLevel(index):
        expRollOver = getPlayerExp(index) - getPlayerNextLevel(index)
        setPlayerLevel(index, getPlayerLevel(index) + 1)

        # get amount of skill points to add
        i = (getPlayerStat(index, Stats.speed) // 10)
        if i < 1:
            i = 1
        elif i > 3:
            i = 3

        setPlayerPoints(index, getPlayerPoints(index) + i)
        setPlayerExp(index, expRollOver)
        globalMsg(getPlayerName(index) + ' has gained a level!', textColor.BRIGHT_BLUE)  # todo: brown color
        playerMsg(index, 'You have gained a level! You now have ' + str(getPlayerPoints(index)) + ' stat points to distribute.', textColor.BRIGHT_BLUE)


def getPlayerVitalRegen(index, vital):
    if not isPlaying(index):
        return 0

    if vital == Vitals.hp:
        i = (getPlayerStat(index, Stats.defense) // 2)

    elif vital == Vitals.mp:
        i = (getPlayerStat(index, Stats.magic) // 2)

    elif vital == Vitals.sp:
        i = (getPlayerStat(index, Stats.speed) // 2)

    if i < 2:
        i == 2

    return i


def onDeath(index):
    # set hp to nothing
    setPlayerVital(index, Vitals.hp, 0)

    # drop all worn items
    for i in range(Equipment.equipment_count):
        if getPlayerEquipmentSlot(index, i) is not None:
            # drop item on map
            print "todo: drop item " + str(i)

    # warp player away
    playerWarp(index, START_MAP, START_X, START_Y)

    # restore vitals
    setPlayerVital(index, Vitals.hp, getPlayerMaxVital(index, Vitals.hp))
    setPlayerVital(index, Vitals.mp, getPlayerMaxVital(index, Vitals.mp))
    setPlayerVital(index, Vitals.sp, getPlayerMaxVital(index, Vitals.sp))
    sendVital(index, Vitals.hp)
    sendVital(index, Vitals.mp)
    sendVital(index, Vitals.sp)

    # if the player that the attacker killed was a pk (player killer) then take it away
    # todo


def damageEquipment(index, equipmentSlot):
    slot = getPlayerEquipmentSlot(index, equipmentSlot)

    if slot is not None:
        setPlayerInvItemDur(index, slot, getPlayerInvItemDur(index, slot) - 1)

        if getPlayerInvItemDur(index, slot) <= 0:
            playerMsg(index, 'Your ' + Item[getPlayerInvItemNum(index, slot)].name + ' has broken.', textColor.YELLOW)
            takeItem(index, getPlayerInvItemNum(index, slot), 0)
        else:
            if getPlayerInvItemDur(index, slot) <= 5:
                playerMsg(index, 'Your ' + Item[getPlayerInvItemNum(index, slot)].name + ' is about to break!', textColor.YELLOW)

        # todo: dont do this? too much back and forth? perhaps dont show durability at all in client
        sendInventoryUpdate(index, slot)


def updateHighIndex():
    # TODO ALOT

    # no players are logged in
    if g.totalPlayersOnline < 1:
        g.highIndex = 0
        g.playersOnline = []
        return

    # reset array
    g.playersOnline = []

    for i in range(0, MAX_PLAYERS):
        if len(getPlayerLogin(i)) > 0:
            g.playersOnline.append(i)
            g.highIndex = i

    packet = json.dumps([{"packet": ServerPackets.SHighIndex, "highindex": g.highIndex}])
    g.conn.sendDataToAll(packet)

    g.serverLogger.info("High Index has been updated")

# (SHOULD BE IN SERVER.TCP?)
####################
# SERVER FUNCTIONS #
####################


def globalMsg(msg, color=(255, 0, 0)):
    packet = json.dumps([{"packet": ServerPackets.SGlobalMsg, "msg": msg, "color": color}])
    g.conn.sendDataToAll(packet)


def adminMsg(msg, color=(255, 0, 0)):
    packet = json.dumps([{"packet": ServerPackets.SAdminMsg, "msg": msg, "color": color}])

    for i in range(g.totalPlayersOnline):
        if getPlayerAccess(playersOnline[i]) > 0:
            g.conn.sendDataTo(playersOnline[i], packet)


def playerMsg(index, msg, color=(255, 0, 0)):
    packet = json.dumps([{"packet": ServerPackets.SPlayerMsg, "msg": msg, "color": color}])
    g.conn.sendDataTo(index, packet)


def mapMsg(mapNum, msg, color=(255, 0, 0)):
    # todo: only current map
    packet = json.dumps([{"packet": ServerPackets.SMapMsg, "msg": msg, "color": color}])
    g.conn.sendDataToMap(mapNum, packet)


def alertMsg(index, reason):
    packet = json.dumps([{"packet": ServerPackets.SAlertMsg, "msg": reason}])
    g.conn.sendDataTo(index, packet)


def isPlaying(index):
    if TempPlayer[index].inGame is True:
        return True


def isLoggedIn(index):
    if len(Player[index].Login) > 0:
        return True


def isMultiAccounts(login):
    for i in range(g.totalPlayersOnline):
        if str(Player[g.playersOnline[i]].Login).lower() == login.lower():
            return True

    return False


def closeConnection(index):
    if index >= 0:
        leftGame(index)

        g.connectionLogger.info("Connection from " + str(index) + " has been terminated.")
        clearPlayer(index)


def createFullMapCache():
    g.serverLogger.debug('createFullMapCache()')
    for i in range(MAX_MAPS):
        mapCacheCreate(i)


def mapCacheCreate(mapNum):
    mapData = []
    mapData.append({"packet": ServerPackets.SMapData, \
                    "mapnum": mapNum, \
                    "mapname": Map[mapNum].name, \
                    "revision": Map[mapNum].revision, \
                    "moral": Map[mapNum].moral, \
                    "tileset": Map[mapNum].tileSet, \
                    "up": Map[mapNum].up, \
                    "down": Map[mapNum].down, \
                    "left": Map[mapNum].left, \
                    "right": Map[mapNum].right, \
                    "bootmap": Map[mapNum].bootMap, \
                    "bootx": Map[mapNum].bootX, \
                    "booty": Map[mapNum].bootY})

    for x in range(MAX_MAPX):
        for y in range(MAX_MAPY):
            tempTile = Map[mapNum].tile[x][y]
            mapData.append([{"ground":    tempTile.ground, \
                             "mask":      tempTile.mask, \
                             "animation": tempTile.anim, \
                             "fringe":    tempTile.fringe, \
                             "type":      tempTile.type, \
                             "data1":     tempTile.data1, \
                             "data2":     tempTile.data2, \
                             "data3":     tempTile.data3}])

    MapCache[mapNum] = mapData


def sendWhosOnline(index):
    msg = ''
    n = 0

    for i in range(g.totalPlayersOnline):
        if g.playersOnline[i] != index:
            msg += getPlayerName(g.playersOnline[i]) + ', '
            n += 1

    if n == 0:
        msg = 'There are no other players online.'
    else:
        msg = 'There are ' + str(n) + ' other players online: ' + msg[:-2] + '.'

    playerMsg(index, msg, whoColor)


def sendChars(index):
    packet = []
    packet.append({"packet": ServerPackets.SAllChars})

    for i in range(0, MAX_CHARS):
        packet.append({"charname": Player[index].char[i].name,
                       "charclass": Class[Player[index].char[i].Class].name,
                       "charlevel": Player[index].char[i].level,
                       "sprite": Player[index].char[i].sprite})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)

def sendJoinMap(index):
    g.serverLogger.debug('sendJoinMap()')
    # send data of all players (on current map) to index
    for i in range(0, g.totalPlayersOnline):
        if g.playersOnline[i] != index:
            if getPlayerMap(g.playersOnline[i]) == getPlayerMap(index):
                packet = json.dumps([{"packet": ServerPackets.SPlayerData, "index": g.playersOnline[i], "name": getPlayerName(g.playersOnline[i]), "access": getPlayerAccess(g.playersOnline[i]), "sprite": getPlayerSprite(g.playersOnline[i]), "map": getPlayerMap(g.playersOnline[i]), "x": getPlayerX(g.playersOnline[i]), "y": getPlayerY(g.playersOnline[i]), "direction": getPlayerDir(g.playersOnline[i])}])
                g.conn.sendDataTo(index, packet)

    # send index's data to all players including himself
    packet = json.dumps([{"packet": ServerPackets.SPlayerData, "index": index, "name": getPlayerName(index),  "access": getPlayerAccess(index), "sprite": getPlayerSprite(index), "map": getPlayerMap(index), "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index)}])
    g.conn.sendDataToMap(getPlayerMap(index), packet)

def sendVital(index, vital):
    if vital == 0:   #hp
        packet = json.dumps([{"packet": ServerPackets.SPlayerHP, "hp_max": getPlayerMaxVital(index, 0), "hp": getPlayerVital(index, 0)}])
    elif vital == 1: #mp
        packet = json.dumps([{"packet": ServerPackets.SPlayerMP, "mp_max": getPlayerMaxVital(index, 1), "mp": getPlayerVital(index, 1)}])
    elif vital == 2: #sp
        packet = json.dumps([{"packet": ServerPackets.SPlayerSP, "sp_max": getPlayerMaxVital(index, 2), "sp": getPlayerVital(index, 2)}])

    g.conn.sendDataTo(index, packet)

def sendStats(index):
    packet = json.dumps([{"packet": ServerPackets.SPlayerStats, "strength": getPlayerStat(index, 0), "defense": getPlayerStat(index, 1), "speed": getPlayerStat(index, 2), "magic": getPlayerStat(index, 3)}])
    g.conn.sendDataTo(index, packet)

def sendWelcome(index):
    playerMsg(index, "Type /help for help on commands. Use arrows keys to move, hold down shift to run, and use ctrl to attack", textColor.CYAN)

    if len(g.MOTD) > 0:
        playerMsg(index, "MOTD: " + g.MOTD, textColor.CYAN)

    #send whos online

def sendClasses(index):
    packet = []
    packet.append({"packet": ServerPackets.SClassesData, "maxclasses": g.maxClasses})

    for i in range(0, g.maxClasses):
        packet.append({"classname": getClassName(i),
                       "sprite": Class[i].sprite,
                       "classmaxhp": getClassMaxVital(i, 0),
                       "classmaxmp": getClassMaxVital(i, 1),
                       "classmaxsp": getClassMaxVital(i, 2),
                       "classstatstr": Class[i].stat[Stats.strength],
                       "classstatdef": Class[i].stat[Stats.defense],
                       "classstatspd": Class[i].stat[Stats.speed],
                       "classstatmag": Class[i].stat[Stats.magic]})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)

def sendNewCharClasses(index):
    packet = []
    packet.append({"packet": ServerPackets.SNewCharClasses, "maxclasses": g.maxClasses})

    for i in range(0, g.maxClasses):
        packet.append({"classname": getClassName(i),
                       "sprite": Class[i].sprite,
                       "classmaxhp": getClassMaxVital(i, 0),
                       "classmaxmp": getClassMaxVital(i, 1),
                       "classmaxsp": getClassMaxVital(i, 2),
                       "classstatstr": Class[i].stat[Stats.strength],
                       "classstatdef": Class[i].stat[Stats.defense],
                       "classstatspd": Class[i].stat[Stats.speed],
                       "classstatmag": Class[i].stat[Stats.magic]})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)


def sendLeaveMap(index, mapNum):
    packet = json.dumps([{"packet": ServerPackets.SLeft, "index": index}])
    g.conn.sendDataToAllBut(index, packet)


def sendPlayerData(index):
    packet = json.dumps([{"packet": ServerPackets.SPlayerData, "index": index, "name": getPlayerName(index), "access": getPlayerAccess(index), "sprite": getPlayerSprite(index), "map": getPlayerMap(index), "x": getPlayerX(index), "y": getPlayerY(index), "direction": getPlayerDir(index)}])
    g.conn.sendDataToMap(getPlayerMap(index), packet)


def sendMap(index, mapNum):
    g.serverLogger.debug('sendMap()')
    g.conn.sendDataTo(index, json.dumps(MapCache[mapNum]))


def sendMapList(index):
    packet = []
    packet.append({"packet": ServerPackets.SMapList})
    print "todo: map editor client"

    mapNames = []
    for i in range(MAX_MAPS):
        mapNames.append(Map[i].name)

    packet.append({'mapnames': mapNames})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)


def sendItems(index):
    for i in range(0, MAX_ITEMS):
        if len(Item[i].name) > 0:
            sendUpdateItemTo(index, i)


def sendInventory(index):
    packet = []
    packet.append({"packet": ServerPackets.SPlayerInv})

    for i in range(0, MAX_INV):
        packet.append({"itemnum": getPlayerInvItemNum(index, i),
                       "itemvalue": getPlayerInvItemValue(index, i),
                       "itemdur": getPlayerInvItemDur(index, i)})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)


def sendInventoryUpdate(index, invSlot):
    packet = json.dumps([{"packet": ServerPackets.SPlayerInvUpdate, "invslot": invSlot, "itemnum": getPlayerInvItemNum(index, invSlot), "itemvalue": getPlayerInvItemValue(index, invSlot), "itemdur": getPlayerInvItemDur(index, invSlot)}])
    g.conn.sendDataTo(index, packet)


def sendWornEquipment(index,):
    packet = json.dumps([{"packet": ServerPackets.SPlayerWornEq, "helmet": getPlayerEquipmentSlot(index, Equipment.helmet), "armor": getPlayerEquipmentSlot(index, Equipment.armor), "weapon": getPlayerEquipmentSlot(index, Equipment.weapon), "shield": getPlayerEquipmentSlot(index, Equipment.shield)}])
    g.conn.sendDataTo(index, packet)


# (SHOULD BE IN datahandler.py)
def sendPlayerDir(index):
    packet = json.dumps([{"packet": ServerPackets.SPlayerDir, "index": index, "direction": getPlayerDir(index)}])
    g.conn.sendDataToAllBut(index, packet)


def sendLeftGame(index):
    #TODO Make name non or smth
    packet = json.dumps([{"packet": ServerPackets.SPlayerData, "index": index, "sprite": 0, "name": "", "access": 0, "map": 0, "x": 0, "y": 0, "direction": 0}])
    g.conn.sendDataToAllBut(index, packet)


def sendUpdateItemToAll(itemNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateItem, "itemnum": itemNum, "itemname": Item[itemNum].name, "itempic": Item[itemNum].pic, "itemtype": Item[itemNum].type, "itemdata1": Item[itemNum].data1, "itemdata2": Item[itemNum].data2, "itemdata3": Item[itemNum].data3}])
    g.conn.sendDataToAll(packet)


def sendUpdateItemTo(index, itemNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateItem, "itemnum": itemNum, "itemname": Item[itemNum].name, "itempic": Item[itemNum].pic, "itemtype": Item[itemNum].type, "itemdata1": Item[itemNum].data1, "itemdata2": Item[itemNum].data2, "itemdata3": Item[itemNum].data3}])
    g.conn.sendDataTo(index, packet)


def sendMapDone(index):
    g.serverLogger.debug('sendMapDone()')
    packet = json.dumps([{"packet": ServerPackets.SMapDone}])
    g.conn.sendDataTo(index, packet)


def sendEditMap(index):
    packet = json.dumps([{"packet": ServerPackets.SEditMap}])
    g.conn.sendDataTo(index, packet)

    #sendMapList(index)


def sendItemEditor(index):
    packet = json.dumps([{"packet": ServerPackets.SItemEditor}])
    g.conn.sendDataTo(index, packet)


def sendEditItem(index):
    packet = json.dumps([{"packet": ServerPackets.SEditItem}])
    g.conn.sendDataTo(index, packet)
