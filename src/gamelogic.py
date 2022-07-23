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
        hackingAttempt(index, 'Position Modification')
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

def castSpell(index, spellSlot):
    if spellSlot < 0 or spellSlot > MAX_PLAYER_SPELLS:
        return

    spellNum = getPlayerSpell(index, spellSlot)
    casted = False

    # make sure player has spell
    if not hasSpell(index, spellNum):
        playerMsg(index, 'You do not have this spell!', textColor.BRIGHT_RED)
        return

    # does not check for level yet

    reqMp = Spell[spellNum].reqMp

    # check if they have enough mp
    if getPlayerVital(index, Vitals.mp) < reqMp:
        playerMsg(index, 'Not enough mana points!', textColor.BRIGHT_RED)
        return

    # check if timer is ok
    tickCount = time.time()*1000
    if tickCount < TempPlayer[index].attackTimer + 1000:
        return

    # ** SELF CAST SPELLS **
    if Spell[spellNum].type == SPELL_TYPE_GIVEITEM:
        n = findOpenInvSlot(index, Spell[spellNum].data1)

        if n is not None:
            giveItem(index, Spell[spellNum].data1, Spell[spellNum].data2)
            mapMsg(getPlayerMap(index), getPlayerMap(index) + ' casts ' + Spell[spellNum].name + '.', textColor.BRIGHT_BLUE)

            # take mana points
            setPlayerVital(index, Vitals.mp, getPlayerVital(index, Vitals.mp) - reqMp)
            sendVital(index, Vitals.mp)

            casted = True

        else:
            playerMsg(index, 'Your inventory is full!', textColor.BRIGHT_RED)

        return

    n = TempPlayer[index].target
    targetType = TempPlayer[index].targetType
    canCast = False

    if targetType == TARGET_TYPE_PLAYER:
        if isPlaying(n):

            if getPlayerVital(index, Vitals.hp) > 0:
                if getPlayerMap(index) == getPlayerMap(n):
                    # check player level?

                    if Map[getPlayerMap(index)].moral == MAP_MORAL_NONE:
                        if getPlayerAccess(index) <= 0:
                            if getPlayerAccess(n) <= 0:
                                if n != index:
                                    canCast = True

            targetName = getPlayerName(n)

            if Spell[spellNum].type == SPELL_TYPE_SUBHP or Spell[spellNum].type == SPELL_TYPE_SUBMP or Spell[spellNum].type == SPELL_TYPE_SUBSP:

                if canCast:
                    if Spell[spellNum].type == SPELL_TYPE_SUBHP:
                        damage = (getPlayerStat(index, Stats.magic) // 4) + Spell[spellNum].data1 - getPlayerProtection(n)

                        if damage > 0:
                            attackPlayer(index, n, damage)

                        else:
                            playerMsg(index, 'The spell was too weak to hurt ' + getPlayerName(n) + '!', textColor.BRIGHT_RED)

                    elif Spell[spellNum].type == SPELL_TYPE_SUBMP:
                        setPlayerVital(n, Vitals.mp, getPlayerVital(n, Vitals.mp) - Spell[spellNum].data1)
                        sendVital(n, Vitals.mp)

                    elif Spell[spellNum].type == SPELL_TYPE_SUBSP:
                        setPlayerVital(n, Vitals.sp, getPlayerVital(n, Vitals.sp) - Spell[spellNum].data1)
                        sendVital(n, vitals.sp)

                    casted = True

            elif Spell[spellNum].type == SPELL_TYPE_ADDHP or Spell[spellNum].type == SPELL_TYPE_ADDMP or Spell[spellNum].type == SPELL_TYPE_ADDSP:
                
                if getPlayerMap(index) == getPlayerMap(n):
                    canCast = True

                if canCast:
                    if Spell[spellNum].type == SPELL_TYPE_ADDHP:
                        setPlayerVital(n, Vitals.hp, getPlayerVital(n, Vitals.hp) + Spell[spellNum].data1)
                        sendVital(n, Vitals.hp)

                    elif Spell[spellNum].type == SPELL_TYPE_ADDMP:
                        setPlayerVital(n, Vitals.mp, getPlayerVital(n, Vitals.mp) + Spell[spellNum].data1)
                        sendVital(n, Vitals.mp)

                    elif Spell[spellNum].type == SPELL_TYPE_ADDSP:
                        setPlayerVital(n, Vitals.sp, getPlayerVital(n, Vitals.sp) + Spell[spellNum].data1)
                        sendVital(n, Vitals.sp)

                    casted = True

    elif targetType == TARGET_TYPE_NPC:
        if NPC[mapNPC[getPlayerMap(index)][n].num].behaviour != NPC_BEHAVIOUR_FRIENDLY and NPC[mapNPC[getPlayerMap(index)][n].num].behaviour != NPC_BEHAVIOUR_SHOPKEEPER:
            canCast = True

        targetName = NPC[mapNPC[getPlayerMap(index)][n].num].name

        if canCast:
            if Spell[spellNum].type == SPELL_TYPE_ADDHP:
                mapNPC[getPlayerMap(index)][n].vital[Vitals.hp] += Spell[spellNum].data1

            elif Spell[spellNum].type == SPELL_TYPE_SUBHP:
                damage = (getPlayerStat(index, Stats.magic) // 4) + Spell[spellNum].data1 - (NPC[mapNPC[getPlayerMap(index)][n].num].stat[Stats.defense] // 2)

                if damage > 0:
                    attackNpc(index, n, damage)

                else:
                    playerMsg(index, 'The spell was too weak to hurt ' + targetName + '!', textColor.BRIGHT_RED)

            elif Spell[spellNum].type == SPELL_TYPE_ADDMP:
                mapNPC[getPlayerMap(index)][n].vital[Vitals.mp] += Spell[spellNum].data1

            elif Spell[spellNum].type == SPELL_TYPE_SUBMP:
                mapNPC[getPlayerMap(index)][n].vital[Vitals.mp] -= Spell[spellNum].data1

            elif Spell[spellNum].type == SPELL_TYPE_ADDSP:
                mapNPC[getPlayerMap(index)][n].vital[Vitals.sp] += Spell[spellNum].data1

            elif Spell[spellNum].type == SPELL_TYPE_SUBSP:
                mapNPC[getPlayerMap(index)][n].vital[Vitals.sp] -= Spell[spellNum].data1

            casted = True

    if casted:
        mapMsg(getPlayerMap(index), getPlayerName(index) + ' casts ' + Spell[spellNum].name + ' on ' + targetName + '.', textColor.BRIGHT_BLUE)
        packet = json.dumps([{"packet": ServerPackets.SCastSpell, "targettype": targetType, "target": n, "spellnum": spellNum}])
        g.conn.sendDataToMap(getPlayerMap(index), packet)

        # take away mana points
        setPlayerVital(index, Vitals.mp, getPlayerVital(index, Vitals.mp) - reqMp)
        sendVital(index, Vitals.mp)

        TempPlayer[index].attackTimer = tickCount
        TempPlayer[index].castedSpell = True

    else:
        playerMsg(index, 'Could not cast spell!', textColor.BRIGHT_RED)

def playerWarp(index, mapNum, x, y):
    if mapNum < 0 or mapNum > MAX_MAPS:
        return

    TempPlayer[index].target = None
    TempPlayer[index].targetType = TARGET_TYPE_NONE

    # check for shop on the map player is leaving and if so say goodbye

    # erase play data to map
    oldMap = getPlayerMap(index)

    if oldMap != mapNum:
        sendLeaveMap(index, oldMap)

    setPlayerMap(index, mapNum)
    setPlayerX(index, x)
    setPlayerY(index, y)

    # check if there is shop on the map and say hello if so

    if getTotalMapPlayers(mapNum) == 0:
        playersOnMap[mapNum] = False

        # regenerate all NPCs health
        for i in range(MAX_MAP_NPCS):
            if mapNPC[oldMap][i].num != None:
                mapNPC[oldMap][i].vital[Vitals.hp] = getNpcMaxVital(mapNPC[oldMap][i].num, Vitals.hp)

    playersOnMap[mapNum] = True

    TempPlayer[index].gettingMap = True

    packet = json.dumps([{"packet": ServerPackets.SCheckForMap, "mapnum": mapNum, "revision": Map[mapNum].revision}])
    g.conn.sendDataTo(index, packet)

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
    sendNpcs(index)
    # shops
    sendSpells(index)
    sendInventory(index)
    sendWornEquipment(index)

    for i in range(0, Vitals.vital_count):  # vital.vital_count -1
        sendVital(index, i)

    sendStats(index)
    sendLevel(index)

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

        if getTotalMapPlayers(getPlayerMap(index)) < 1:
            playersOnMap[getPlayerMap(index)] = False

        savePlayer(index)

        # send global msg that player left game
        if getPlayerAccess(index) <= ADMIN_MONITOR:
            globalMsg(getPlayerName(index) + ' has left ' + GAME_NAME + '!', joinLeftColor)
        else:
            globalMsg(getPlayerName(index) + ' has left ' + GAME_NAME + '!', textColor.WHITE)

        g.connectionLogger.info(getPlayerName(index) + ' has disconnected')
        sendLeftGame(index)

        g.totalPlayersOnline -= 1
        clearPlayer(index)
        updateHighIndex()

    clearPlayer(index)


def findPlayer(name):
    for i in range(g.totalPlayersOnline):
        # dont check a name that is too small
        if len(getPlayerName(g.playersOnline[i])) >= len(name):
            if getPlayerName(g.playersOnline[i]).lower() == name.lower():
                return g.playersOnline[i]

    return None


def findOpenMapItemSlot(mapNum):
    if mapNum is None or mapNum > MAX_MAPS:
        return

    for i in range(MAX_MAP_ITEMS):
        if mapItem[mapNum][i].num is None:
            return i

def spawnItem(itemNum, itemVal, mapNum, x, y):
    if itemNum is None or itemNum > MAX_ITEMS or mapNum is None or mapNum > MAX_MAPS:
        return

    # find open map item slot
    i = findOpenMapItemSlot(mapNum)

    spawnItemSlot(i, itemNum, itemVal, Item[itemNum].data1, mapNum, x, y)

def spawnItemSlot(mapItemSlot, itemNum, itemVal, itemDur, mapNum, x, y):
    if mapItemSlot is None or mapItemSlot > MAX_MAP_ITEMS or itemNum > MAX_ITEMS or mapNum is None or mapNum > MAX_MAPS:
        return

    i = mapItemSlot

    if i != None:
        if itemNum <= MAX_ITEMS:
            mapItem[mapNum][i].num = itemNum
            mapItem[mapNum][i].value = itemVal

            if itemNum != None:
                if (Item[itemNum].type >= ITEM_TYPE_WEAPON) and (Item[itemNum].type <= ITEM_TYPE_SHIELD):
                    mapItem[mapNum][i].dur = itemDur
                else:
                    mapItem[mapNum][i].dur = 0
            else:
                mapItem[mapNum][i].dur = 0

            mapItem[mapNum][i].x = x
            mapItem[mapNum][i].y = y

            packet = json.dumps([{"packet": ServerPackets.SSpawnItem, "slot": i, "itemnum": itemNum, "itemval": itemVal, "itemdur": mapItem[mapNum][i].dur, "x": x, "y": y,}])
            g.conn.sendDataToMap(mapNum, packet)

def spawnMapItems(mapNum):
    if mapNum is None or mapNum > MAX_MAPS:
        return

    for x in range(MAX_MAPX):
        for y in range(MAX_MAPY):
            # check if tile type is an item or a saved tile incase someone drops something
            if Map[mapNum].tile[x][y].type == TILE_TYPE_ITEM:

                # check if currency and if they set the value to 0, set it to 1 automatically
                if Item[Map[mapNum].tile[x][y].data1].type == ITEM_TYPE_CURRENCY and Map[mapNum].tile[x][y].data2 == 0:
                    spawnItem(Map[mapNum].tile[x][y].data1, 1, mapNum, x, y)
                else:
                    spawnItem(Map[mapNum].tile[x][y].data1, Map[mapNum].tile[x][y].data2, mapNum, x, y)


def spawnAllMapsItems():
    for i in range(MAX_MAPS):
        spawnMapItems(i)

def spawnNpc(mapNpcNum, mapNum):
    if mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or mapNum < 0 or mapNum > MAX_MAPS:
        return

    npcNum = Map[mapNum].npc[mapNpcNum]

    if npcNum is not None:
        mapNPC[mapNum][mapNpcNum].num = npcNum
        mapNPC[mapNum][mapNpcNum].target = None

        mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] = getNpcMaxVital(npcNum, Vitals.hp)
        mapNPC[mapNum][mapNpcNum].vital[Vitals.mp] = getNpcMaxVital(npcNum, Vitals.mp)
        mapNPC[mapNum][mapNpcNum].vital[Vitals.sp] = getNpcMaxVital(npcNum, Vitals.sp)

        mapNPC[mapNum][mapNpcNum].dir = random.randint(0, 3)

        for i in range(100):
            x = random.randint(0, MAX_MAPX-1)
            y = random.randint(0, MAX_MAPY-1)

            # check if tile is walkable
            if Map[mapNum].tile[x][y].type == TILE_TYPE_WALKABLE:
                mapNPC[mapNum][mapNpcNum].x = x
                mapNPC[mapNum][mapNpcNum].y = y
                spawned = True

        # didn't spawn, so now we'll just try to find a free tile
        if not spawned:
            for x in range(MAX_MAPX):
                for y in range(MAX_MAPY):
                    if Map[mapNum].tile[x][y].type == TILE_TYPE_WALKABLE:
                        mapNPC[mapNum][mapNpcNum].x = x
                        mapNPC[mapNum][mapNpcNum].y = y
                        spawned = True

        # if we succeded, then send it to everybody
        if spawned:
            sendNpcSpawn(mapNpcNum, mapNum)

def spawnMapNpcs(mapNum):
    for i in range(MAX_MAP_NPCS):
        spawnNpc(i, mapNum)

def spawnAllMapNpcs():
    for i in range(MAX_MAPS):
        spawnMapNpcs(i)

def canNpcMove(mapNum, mapNpcNum, direction):
    if mapNum < 0 or mapNum > MAX_MAPS or mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or direction < DIR_UP or direction > DIR_RIGHT:
        return

    x = mapNPC[mapNum][mapNpcNum].x
    y = mapNPC[mapNum][mapNpcNum].y

    if direction == DIR_UP:
        if y > 0:
            n = Map[mapNum].tile[x][y-1].type

            # check to make sure tile is walkable
            if n != TILE_TYPE_WALKABLE:
                return False

            # make sure player is not in the way
            for i in range(g.totalPlayersOnline):
                if getPlayerMap(g.playersOnline[i]) == mapNum:
                    if getPlayerX(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].x:
                        if getPlayerY(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].y-1:
                            return False

            # make sure npc is not in the way
            for i in range(MAX_MAP_NPCS):
                if i != mapNpcNum:
                    if mapNPC[mapNum][i].num != None:
                        if mapNPC[mapNum][i].x == mapNPC[mapNum][mapNpcNum].x:
                            if mapNPC[mapNum][i].y == mapNPC[mapNum][mapNpcNum].y-1:
                                return False
        else:
            return False

    elif direction == DIR_DOWN:
        if y < MAX_MAPY-1:
            n = Map[mapNum].tile[x][y+1].type

            # check to make sure tile is walkable
            if n != TILE_TYPE_WALKABLE:
                return False

            # make sure player is not in the way
            for i in range(g.totalPlayersOnline):
                if getPlayerMap(g.playersOnline[i]) == mapNum:
                    if getPlayerX(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].x:
                        if getPlayerY(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].y+1:
                            return False

            # make sure npc is not in the way
            for i in range(MAX_MAP_NPCS):
                if i != mapNpcNum:
                    if mapNPC[mapNum][i].num != None:
                        if mapNPC[mapNum][i].x == mapNPC[mapNum][mapNpcNum].x:
                            if mapNPC[mapNum][i].y == mapNPC[mapNum][mapNpcNum].y+1:
                                return False
        else:
            return False

    elif direction == DIR_LEFT:
        if x > 0:
            n = Map[mapNum].tile[x-1][y].type

            # check to make sure tile is walkable
            if n != TILE_TYPE_WALKABLE:
                return False

            # make sure player is not in the way
            for i in range(g.totalPlayersOnline):
                if getPlayerMap(g.playersOnline[i]) == mapNum:
                    if getPlayerX(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].x-1:
                        if getPlayerY(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].y:
                            return False

            # make sure npc is not in the way
            for i in range(MAX_MAP_NPCS):
                if i != mapNpcNum:
                    if mapNPC[mapNum][i].num != None:
                        if mapNPC[mapNum][i].x == mapNPC[mapNum][mapNpcNum].x-1:
                            if mapNPC[mapNum][i].y == mapNPC[mapNum][mapNpcNum].y:
                                return False
        else:
            return False

    elif direction == DIR_RIGHT:
        if x < MAX_MAPX-1:
            n = Map[mapNum].tile[x+1][y].type

            # check to make sure tile is walkable
            if n != TILE_TYPE_WALKABLE:
                return False

            # make sure player is not in the way
            for i in range(g.totalPlayersOnline):
                if getPlayerMap(g.playersOnline[i]) == mapNum:
                    if getPlayerX(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].x+1:
                        if getPlayerY(g.playersOnline[i]) == mapNPC[mapNum][mapNpcNum].y:
                            return False

            # make sure npc is not in the way
            for i in range(MAX_MAP_NPCS):
                if i != mapNpcNum:
                    if mapNPC[mapNum][i].num != None:
                        if mapNPC[mapNum][i].x == mapNPC[mapNum][mapNpcNum].x+1:
                            if mapNPC[mapNum][i].y == mapNPC[mapNum][mapNpcNum].y:
                                return False
        else:
            return False

    return True

def npcMove(mapNum, mapNpcNum, direction, movement):
    if mapNum < 0 or mapNum > MAX_MAPS or mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or direction < DIR_UP or direction > DIR_RIGHT:
        return

    mapNPC[mapNum][mapNpcNum].dir = direction

    if direction == DIR_UP:
        mapNPC[mapNum][mapNpcNum].y -= 1
        sendNpcMove(mapNpcNum, movement, mapNum)

    elif direction == DIR_DOWN:
        mapNPC[mapNum][mapNpcNum].y += 1
        sendNpcMove(mapNpcNum, movement, mapNum)

    elif direction == DIR_LEFT:
        mapNPC[mapNum][mapNpcNum].x -= 1
        sendNpcMove(mapNpcNum, movement, mapNum)

    elif direction == DIR_RIGHT:
        mapNPC[mapNum][mapNpcNum].x += 1
        sendNpcMove(mapNpcNum, movement, mapNum)

def npcDir(mapNum, mapNpcNum, direction):
    if mapNum < 0 or mapNum > MAX_MAPS or mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or direction < DIR_UP or direction > DIR_RIGHT:
        return

    mapNPC[mapNum][mapNpcNum].dir = direction

    packet = json.dumps([{"packet": ServerPackets.SNpcDir, "mapnpcnum": mapNpcNum, "direction": direction}])
    g.conn.sendDataToMap(mapNum, packet)


def canAttackNpc(attacker, mapNpcNum):
    if not isPlaying(attacker) or mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS:
        return

    if mapNPC[getPlayerMap(attacker)][mapNpcNum].num is None:
        return

    mapNum = getPlayerMap(attacker)
    npcNum = mapNPC[getPlayerMap(attacker)][mapNpcNum].num

    # make sure npc isnt already dead
    if mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] <= 0:
        return

    # make sure they are on the same map
    tickCount = time.time() * 1000
    if isPlaying(attacker):
        if npcNum is not None and tickCount > TempPlayer[attacker].attackTimer + 1000:
            # check if at same coordinates

            direction = getPlayerDir(attacker)

            if direction == DIR_UP:
                npcX = mapNPC[mapNum][mapNpcNum].x
                npcY = mapNPC[mapNum][mapNpcNum].y + 1

            elif direction == DIR_DOWN:
                npcX = mapNPC[mapNum][mapNpcNum].x
                npcY = mapNPC[mapNum][mapNpcNum].y - 1

            elif direction == DIR_LEFT:
                npcX = mapNPC[mapNum][mapNpcNum].x + 1
                npcY = mapNPC[mapNum][mapNpcNum].y

            elif direction == DIR_RIGHT:
                npcX = mapNPC[mapNum][mapNpcNum].x - 1
                npcY = mapNPC[mapNum][mapNpcNum].y

            if npcX == getPlayerX(attacker) and npcY == getPlayerY(attacker):
                if NPC[npcNum].behaviour != NPC_BEHAVIOUR_FRIENDLY and NPC[npcNum].behaviour != NPC_BEHAVIOUR_SHOPKEEPER:
                    return True
                else:
                    playerMsg(attacker, 'You cannot attack a ' + NPC[npcNum].name + '!', textColor.BRIGHT_BLUE)

def attackNpc(attacker, mapNpcNum, damage):
    if not isPlaying(attacker) or mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or damage < 0:
        return

    mapNum = getPlayerMap(attacker)
    npcNum = mapNPC[getPlayerMap(attacker)][mapNpcNum].num
    name = NPC[npcNum].name

    # send packet so they can see attacker attacking
    packet = json.dumps([{"packet": ServerPackets.SAttack, "attacker": attacker}])
    g.conn.sendDataToMapBut(getPlayerMap(attacker), attacker, packet)

    # check for weapon
    weaponNum = None
    if getPlayerEquipmentSlot(attacker, Equipment.weapon) != None:
        weaponNum = getPlayerInvItemNum(attacker, getPlayerEquipmentSlot(attacker, Equipment.weapon))

    if damage >= mapNPC[mapNum][mapNpcNum].vital[Vitals.hp]:
        # check for a weapon and say damage
        if weaponNum is not None:
            # weapon is equipped
            playerMsg(attacker, 'You hit a ' + name + ' with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points, killing it.', textColor.BRIGHT_RED)

        else:
            playerMsg(attacker, 'You hit a ' + name + ' for ' + str(damage) + ' hit points, killing it.', textColor.BRIGHT_RED)

        # calculate exp to give attacker
        statStr = NPC[npcNum].stat[Stats.strength]
        statDef = NPC[npcNum].stat[Stats.defense]
        exp = statStr * statDef * 2

        if exp < 0:
            exp = 1

        # check if in party, if so divide exp up by 2
        if not TempPlayer[attacker].inParty:
            setPlayerExp(attacker, getPlayerExp(attacker) + exp)
            playerMsg(attacker, 'You have agained ' + str(exp) + ' experience points.', textColor.BRIGHT_BLUE)

        else:
            # player is in party
            print('player is in party, todo')

        # drop loot if they have it
        n = random.randint(1, NPC[npcNum].dropChance)

        if n == 1:
            spawnItem(NPC[npcNum].dropItem, NPC[npcNum].dropItemValue, mapNum, mapNPC[mapNum][mapNpcNum].x, mapNPC[mapNum][mapNpcNum].y)

        # now set hp to 0 so we kill them in the server loop
        mapNPC[mapNum][mapNpcNum].num = None
        mapNPC[mapNum][mapNpcNum].spawnWait = time.time() * 1000
        mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] = 0

        # send packet that npc is dead to map
        packet = json.dumps([{"packet": ServerPackets.SNpcDead, "mapnpcnum": mapNpcNum}])
        g.conn.sendDataToMap(getPlayerMap(attacker), packet)

        # check for level up
        checkPlayerLevelUp(attacker)

        # check for level up party member
        # todo

        # check if target is npc that died, and if so, set target to 0
        # todo

    else:
        # npc not dead, just do damage
        mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] = mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] - damage

        # check for a weapon and say damage
        if weaponNum is not None:
            # weapon is equipped
            playerMsg(attacker, 'You hit a ' + name + ' with a ' + Item[weaponNum].name + ' for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

        else:
            playerMsg(attacker, 'You hit a ' + name + ' for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

        # check if we should send a message
        if mapNPC[mapNum][mapNpcNum].target is None:
            if len(NPC[npcNum].attackSay) > 0:
                playerMsg(attacker, 'A ' + NPC[npcNum].name + ' says, ' + NPC[npcNum].attackSay + ' to you.', sayColor)

        # set npc to target player
        mapNPC[mapNum][mapNpcNum].target = attacker

        # now check for guard ai and if so have all on map guards after the player
        if NPC[mapNPC[mapNum][mapNpcNum].num].behaviour == NPC_BEHAVIOUR_GUARD:
            for i in range(MAX_MAP_NPCS):
                if mapNPC[mapNum][i].num == mapNPC[mapNum][mapNpcNum].num:
                    mapNPC[mapNum][i].target = attacker

    # reduce durability on weapon
    damageEquipment(attacker, Equipment.weapon)

    # reset attack timer
    TempPlayer[attacker].attackTimer = time.time()


def canNpcAttackPlayer(mapNpcNum, index):
    if mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or not isPlaying(index):
        return

    if mapNPC[getPlayerMap(index)][mapNpcNum].num is None:
        return

    mapNum = getPlayerMap(index)
    npcNum = mapNPC[getPlayerMap(index)][mapNpcNum].num

    # make sure npc isnt already dead
    if mapNPC[mapNum][mapNpcNum].vital[Vitals.hp] <= 0:
        return

    # make sure npcs dont attack more than once a second
    tickCount = time.time() * 1000

    if tickCount < mapNPC[mapNum][mapNpcNum].attackTimer + 1000:
        return

    # make sure we dont attack players that are switiching maps
    if TempPlayer[index].gettingMap:
        return

    mapNPC[mapNum][mapNpcNum].attackTimer = tickCount

    # make sure they are on the same map
    if isPlaying(index):
        if npcNum is not None:
            # check if at same coordinates
            if getPlayerY(index) + 1 == mapNPC[mapNum][mapNpcNum].y and getPlayerX(index) == mapNPC[mapNum][mapNpcNum].x:
                return True

            elif getPlayerY(index) - 1 == mapNPC[mapNum][mapNpcNum].y and getPlayerX(index) == mapNPC[mapNum][mapNpcNum].x:
                return True

            elif getPlayerY(index) == mapNPC[mapNum][mapNpcNum].y and getPlayerX(index) + 1 == mapNPC[mapNum][mapNpcNum].x:
                return True

            elif getPlayerY(index) == mapNPC[mapNum][mapNpcNum].y and getPlayerX(index) - 1 == mapNPC[mapNum][mapNpcNum].x:
                return True

def npcAttackPlayer(mapNpcNum, victim, damage):
    if mapNpcNum < 0 or mapNpcNum > MAX_MAP_NPCS or not isPlaying(victim) or damage < 0:
        return

    if mapNPC[getPlayerMap(victim)][mapNpcNum].num is None:
        return

    mapNum = getPlayerMap(victim)
    name = NPC[mapNPC[mapNum][mapNpcNum].num].name

    # send this packet so they can see npc attacking

    # reduce durability on victims equipment
    damageEquipment(victim, Equipment.armor)
    damageEquipment(victim, Equipment.helmet)

    if damage >= getPlayerVital(victim, Vitals.hp):
        # say damage
        playerMsg(victim, 'A ' + name + ' hit you for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

        # player is dead
        globalMsg(getPlayerName(victim) + ' has been killed by a ' + name, textColor.BRIGHT_RED)

        # calculate exp to give attacker
        exp = getPlayerExp(victim) // 3

        # make sure we dont get less than 0
        if exp < 0:
            exp = 0

        if exp == 0:
            playerMsg(victim, 'You lost no experience points.', textColor.BRIGHT_RED)
        else:
            setPlayerExp(victim, getPlayerExp(victim) - exp)
            playerMsg(victim, 'You lost ' + str(exp) + ' experience points.', textColor.BRIGHT_RED)

        # set npc target to noone
        mapNPC[mapNum][mapNpcNum].target = None

        onDeath(victim)

    else:
        # player not dead, just do damage
        setPlayerVital(victim, Vitals.hp, getPlayerVital(victim, Vitals.hp) - damage)
        sendVital(victim, Vitals.hp)

        # say damage
        playerMsg(victim, 'A ' + name + ' hit you for ' + str(damage) + ' hit points.', textColor.BRIGHT_RED)

def getTotalMapPlayers(mapNum):
    n = 0
    for i in range(len(g.playersOnline)):
        if isPlaying(g.playersOnline[i]) and getPlayerMap(g.playersOnline[i]) == mapNum:
            n += 1

    return n

def getNpcMaxVital(npcNum, vital):
    if npcNum < 0 or npcNum > MAX_NPCS:
        return 0

    if vital == Vitals.hp:
        statStr = NPC[npcNum].stat[Stats.strength]
        statDef = NPC[npcNum].stat[Stats.defense]
        return statStr * statDef

    elif vital == Vitals.mp:
        return NPC[npcNum].stat[Stats.magic] * 2

    elif vital == Vitals.sp:
        return NPC[npcNum].stat[Stats.speed] * 2


def getNpcVitalRegen(npcNum, vital):
    if npcNum < 0 or npcNum > MAX_NPCS:
        return 0

    if vital == Vitals.hp:
        i = NPC[npcNum].stat[Stats.defense] // 3
        if i < 1:
            i = 1

        return i

    #elif vital == vitals.mp:

    #elif vital == vitals.sp:


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

def findOpenSpellSlot(index):
    for i in range(MAX_PLAYER_SPELLS):
        if getPlayerSpell(index, i) is None:
            return i

    return None

def hasSpell(index, spellNum):
    for i in range(MAX_PLAYER_SPELLS):
        if getPlayerSpell(index, i) == spellNum:
            return True

    return False

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


def playerMapGetItem(index):
    if not isPlaying(index):
        return

    mapNum = getPlayerMap(index)

    for i in range(MAX_MAP_ITEMS):
        # see if theres an item here
        if mapItem[mapNum][i].num <= MAX_ITEMS:
            # check if item is at same location as the player
            if mapItem[mapNum][i].x == getPlayerX(index) and mapItem[mapNum][i].y == getPlayerY(index):
                # find open slot
                n = findOpenInvSlot(index, mapItem[mapNum][i].num)

                # open slot available?
                if n is not None:
                    # give item to player
                    setPlayerInvItemNum(index, n, mapItem[mapNum][i].num)

                    # is the item a currency?
                    if Item[getPlayerInvItemNum(index, n)].type == ITEM_TYPE_CURRENCY:
                        setPlayerInvItemValue(index, n, getPlayerInvItemValue(index, n) + mapItem[mapNum][i].value)
                        msg = 'You picked up ' + str(mapItem[mapNum][i].value) + ' ' + Item[getPlayerInvItemNum(index, n)].name + '.'

                    else:
                        setPlayerInvItemValue(index, n, 0)
                        msg = 'You picked up a ' + Item[getPlayerInvItemNum(index, n)].name

                    setPlayerInvItemDur(index, n, mapItem[mapNum][i].dur)

                    # erase item from map
                    mapItem[mapNum][i].num = None
                    mapItem[mapNum][i].value = None
                    mapItem[mapNum][i].dur = None
                    mapItem[mapNum][i].x = None
                    mapItem[mapNum][i].y = None

                    sendInventoryUpdate(index, n)
                    spawnItemSlot(i, None, None, None, getPlayerMap(index), None, None)
                    playerMsg(index, msg, textColor.YELLOW)
                    break

                else:
                    playerMsg(index, 'Your inventory is full.', textColor.BRIGHT_RED)
                    break

def playerMapDropItem(index, invNum, amount):
    if not isPlaying(index) or invNum < 0 or invNum > MAX_INV:
        return

    if getPlayerInvItemNum(index, invNum) is not None:
        if getPlayerInvItemNum(index, invNum) <= MAX_ITEMS:
            i = findOpenMapItemSlot(getPlayerMap(index))

            if i is not None:
                mapItem[getPlayerMap(index)][i].dur = 0

                # check if its any sort of armor or weapon
                itemType = Item[getPlayerInvItemNum(index, invNum)].type

                if itemType == ITEM_TYPE_ARMOR:
                    if invNum == getPlayerEquipmentSlot(index, Equipment.armor):
                        setPlayerEquipmentSlot(index, 0, Equipment.armor)
                        sendWornEquipment(index)

                    mapItem[getPlayerMap(index)][i].dur = getPlayerInvItemDur(index, invNum)

                elif itemType == ITEM_TYPE_WEAPON:
                    if invNum == getPlayerEquipmentSlot(index, Equipment.weapon):
                        setPlayerEquipmentSlot(index, 0, Equipment.weapon)
                        sendWornEquipment(index)

                    mapItem[getPlayerMap(index)][i].dur = getPlayerInvItemDur(index, invNum)

                elif itemType == ITEM_TYPE_HELMET:
                    if invNum == getPlayerEquipmentSlot(index, Equipment.helmet):
                        setPlayerEquipmentSlot(index, 0, Equipment.helmet)
                        sendWornEquipment(index)

                    mapItem[getPlayerMap(index)][i].dur = getPlayerInvItemDur(index, invNum)

                elif itemType == ITEM_TYPE_SHIELD:
                    if invNum == getPlayerEquipmentSlot(index, Equipment.shield):
                        setPlayerEquipmentSlot(index, 0, Equipment.shield)
                        sendWornEquipment(index)

                    mapItem[getPlayerMap(index)][i].dur = getPlayerInvItemDur(index, invNum)

                mapItem[getPlayerMap(index)][i].num = getPlayerInvItemNum(index, invNum)
                mapItem[getPlayerMap(index)][i].x = getPlayerX(index)
                mapItem[getPlayerMap(index)][i].y = getPlayerY(index)

                if itemType == ITEM_TYPE_CURRENCY:
                    # check if its more than they have, and if so drop it
                    if amount >= getPlayerInvItemValue(index, invNum):
                        mapItem[getPlayerMap(index)][i].value = getPlayerInvItemValue(index, invNum)
                        
                        mapMsg(getPlayerMap(index), getPlayerName(index) + ' drops ' + str(getPlayerInvItemValue(index, invNum)) + ' ' + Item[getPlayerInvItemNum(index, invNum)].name + '.', textColor.YELLOW)

                        setPlayerInvItemNum(index, invNum, None)
                        setPlayerInvItemValue(index, invNum, 0)
                        setPlayerInvItemDur(index, invNum, 0)

                    else:
                        mapItem[getPlayerMap(index)][i].value = amount

                        mapMsg(getPlayerMap(index), getPlayerName(index) + ' drops ' + str(amount) + ' ' + Item[getPlayerInvItemNum(index, invNum)].name + '.', textColor.YELLOW)

                        setPlayerInvItemValue(index, invNum, getPlayerInvItemValue(index, invNum) - amount)

                else:
                    # its not a currency
                    mapItem[getPlayerMap(index)][i].value = 0

                    # msg todo

                    setPlayerInvItemNum(index, invNum, None)
                    setPlayerInvItemValue(index, invNum, 0)
                    setPlayerInvItemDur(index, invNum, 0)

                # send inventory update
                sendInventoryUpdate(index, invNum)

                # spawn item
                spawnItemSlot(i, mapItem[getPlayerMap(index)][i].num, amount, mapItem[getPlayerMap(index)][i].dur, getPlayerMap(index), getPlayerX(index), getPlayerY(index))

            else:
                playerMsg(index, 'Too many items already on the ground.', textColor.BRIGHT_RED)




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

    sendLevel(index)


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
            playerMapDropItem(index, getPlayerEquipmentSlot(index, i), 0)

    # warp player away
    playerWarp(index, START_MAP, START_X, START_Y)

    # restore vitals
    setPlayerVital(index, Vitals.hp, getPlayerMaxVital(index, Vitals.hp))
    setPlayerVital(index, Vitals.mp, getPlayerMaxVital(index, Vitals.mp))
    setPlayerVital(index, Vitals.sp, getPlayerMaxVital(index, Vitals.sp))
    sendVital(index, Vitals.hp)
    sendVital(index, Vitals.mp)
    sendVital(index, Vitals.sp)

    sendLevel(index)

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

            if len(g.playersOnline) >= g.totalPlayersOnline:
                break

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

def hackingAttempt(index, reason):
    if index is not None:
        if isPlaying(index):
            globalMsg(getPlayerLogin(index) + '/' + getPlayerName(index) + ' has been booted for (' + reason +')', textColor.WHITE)

        alertMsg(index, 'You have lost your connection with ' + GAME_NAME + '.')
        g.conn.closeConnection(index)


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
            mapData.append([{"layer1":    tempTile.layer1, \
                             "layer2":    tempTile.layer2, \
                             "layer3":    tempTile.layer3, \
                             "mask":      tempTile.mask, \
                             "animation": tempTile.anim, \
                             "fringe":    tempTile.fringe, \
                             "type":      tempTile.type, \
                             "data1":     tempTile.data1, \
                             "data2":     tempTile.data2, \
                             "data3":     tempTile.data3}])

    for i in range(MAX_MAP_NPCS):
        mapData.append([{"npc": Map[mapNum].npc[i]}])

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

def sendLevel(index):
    packet = json.dumps([{"packet": ServerPackets.SPlayerLevel, "level": getPlayerLevel(index), "exp": getPlayerExp(index), "exptolevel": getPlayerNextLevel(index)}])
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

    mapNames = []
    for i in range(MAX_MAPS):
        mapNames.append(Map[i].name)

    packet.append({'mapnames': mapNames})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)

def sendMapItemsTo(index, mapNum):
    packet = []
    packet.append({"packet": ServerPackets.SMapItemData})

    for i in range(MAX_MAP_ITEMS):
        packet.append({"itemnum": mapItem[mapNum][i].num,
                       "itemval": mapItem[mapNum][i].value,
                       "itemdur": mapItem[mapNum][i].dur,
                       "x":       mapItem[mapNum][i].x,
                       "y":       mapItem[mapNum][i].y})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)

def sendMapItemsToAll(mapNum):
    packet = []
    packet.append({"packet": ServerPackets.SMapItemData})

    for i in range(MAX_MAP_ITEMS):
        packet.append({"itemnum": mapItem[mapNum][i].num,
                       "itemval": mapItem[mapNum][i].value,
                       "itemdur": mapItem[mapNum][i].dur,
                       "x":       mapItem[mapNum][i].x,
                       "y":       mapItem[mapNum][i].y})

    nPacket = json.dumps(packet)
    g.conn.sendDataToMap(mapNum, nPacket)


def sendMapNpcsTo(index, mapNum):
    packet = []
    packet.append({"packet": ServerPackets.SMapNpcData})

    for i in range(MAX_MAP_NPCS):
        packet.append({"num": mapNPC[mapNum][i].num,
                       "x":   mapNPC[mapNum][i].x,
                       "y":   mapNPC[mapNum][i].y,
                       "dir": mapNPC[mapNum][i].dir})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)


def sendMapNpcsToMap(mapNum):
    packet = []
    packet.append({"packet": ServerPackets.SMapNpcData})

    for i in range(MAX_MAP_NPCS):
        packet.append({"num": mapNPC[mapNum][i].num,
                       "x":   mapNPC[mapNum][i].x,
                       "y":   mapNPC[mapNum][i].y,
                       "dir": mapNPC[mapNum][i].dir})

    nPacket = json.dumps(packet)
    g.conn.sendDataToMap(mapNum, nPacket)

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

def sendPlayerXY(index):
    packet = json.dumps([{'packet': ServerPackets.SPlayerXY, 'x': getPlayerX(index), 'y': getPlayerY(index)}])
    g.conn.sendDataTo(index, packet)

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

    sendMapList(index)


def sendItemEditor(index):
    packet = json.dumps([{"packet": ServerPackets.SItemEditor}])
    g.conn.sendDataTo(index, packet)


def sendEditItem(index):
    packet = json.dumps([{"packet": ServerPackets.SEditItem}])
    g.conn.sendDataTo(index, packet)

def sendSpellEditor(index):
    packet = json.dumps([{"packet": ServerPackets.SSpellEditor}])
    g.conn.sendDataTo(index, packet)

def sendEditSpellTo(index, spellNum):
    packet = json.dumps([{"packet": ServerPackets.SEditSpell, "spellnum": spellNum, "spellname": Spell[spellNum].name, "pic": Spell[spellNum].pic, "reqmp": Spell[spellNum].reqMp, 'reqclass': Spell[spellNum].reqClass, 'reqlevel': Spell[spellNum].reqLevel, 'type': Spell[spellNum].type, 'data1': Spell[spellNum].data1, 'data2': Spell[spellNum].data2, 'data3': Spell[spellNum].data3}])
    g.conn.sendDataTo(index, packet)

def sendSpells(index):
    for i in range(MAX_SPELLS):
        if len(Spell[i].name) > 0:
            sendUpdateSpellTo(index, i)

def sendPlayerSpells(index):
    packet = []
    packet.append({"packet": ServerPackets.SSpells})

    for i in range(0, MAX_PLAYER_SPELLS):
        if getPlayerSpell(index, i) is not None:
            packet.append({"slot": i,
                           "spellnum": getPlayerSpell(index, i)})

    nPacket = json.dumps(packet)
    g.conn.sendDataTo(index, nPacket)

def sendUpdateSpellToAll(spellNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateSpell, "spellnum": spellNum, "spellname": Spell[spellNum].name, "pic": Spell[spellNum].pic, "reqmp": Spell[spellNum].reqMp, 'type': Spell[spellNum].type, 'data1': Spell[spellNum].data1}])
    g.conn.sendDataToAll(packet)

def sendUpdateSpellTo(index, spellNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateSpell, "spellnum": spellNum, "spellname": Spell[spellNum].name, "pic": Spell[spellNum].pic, "reqmp": Spell[spellNum].reqMp, 'type': Spell[spellNum].type, 'data1': Spell[spellNum].data1}])
    g.conn.sendDataTo(index, packet)

def sendNpcs(index):
    for i in range(MAX_NPCS):
        if len(NPC[i].name) > 0:
            sendUpdateNpcTo(index, i)

def sendNpcSpawn(mapNpcNum, mapNum):
    packet = json.dumps([{"packet": ServerPackets.SSpawnNpc, 'mapnpcnum': mapNpcNum, 'num': mapNPC[mapNum][mapNpcNum].num, 'x': mapNPC[mapNum][mapNpcNum].x, 'y': mapNPC[mapNum][mapNpcNum].y, 'dir': mapNPC[mapNum][mapNpcNum].dir}])
    g.conn.sendDataToMap(mapNum, packet)

def sendNpcMove(mapNpcNum, movement, mapNum):
    packet = json.dumps([{"packet": ServerPackets.SNpcMove, 'mapnpcnum': mapNpcNum, 'x': mapNPC[mapNum][mapNpcNum].x, 'y': mapNPC[mapNum][mapNpcNum].y, 'dir': mapNPC[mapNum][mapNpcNum].dir, 'movement': movement}])
    g.conn.sendDataToMap(mapNum, packet)

def sendUpdateNpcToAll(npcNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateNpc, 'npcnum': npcNum, 'name': NPC[npcNum].name, 'sprite': NPC[npcNum].sprite}])
    g.conn.sendDataToAll(packet)

def sendUpdateNpcTo(index, npcNum):
    packet = json.dumps([{"packet": ServerPackets.SUpdateNpc, 'npcnum': npcNum, 'name': NPC[npcNum].name, 'sprite': NPC[npcNum].sprite}])
    g.conn.sendDataTo(index, packet)

def sendEditNpcTo(index, npcNum):
    packet = json.dumps([{"packet": ServerPackets.SEditNpc, 'npcnum': npcNum, 'name': NPC[npcNum].name, 'attacksay': NPC[npcNum].attackSay, 'sprite': NPC[npcNum].sprite, 'spawnsec': NPC[npcNum].spawnSecs, 'behavior': NPC[npcNum].behaviour, 'range': NPC[npcNum].range, \
                                                            'dropchance': NPC[npcNum].dropChance, 'dropitem': NPC[npcNum].dropItem, 'dropitemval': NPC[npcNum].dropItemValue, \
                                                            'strength': NPC[npcNum].stat[Stats.strength], 'defense': NPC[npcNum].stat[Stats.defense], 'magic': NPC[npcNum].stat[Stats.magic], 'speed': NPC[npcNum].stat[Stats.speed]}])
    g.conn.sendDataTo(index, packet)


def sendNpcEditor(index):
    packet = json.dumps([{"packet": ServerPackets.SNpcEditor}])
    g.conn.sendDataTo(index, packet)
