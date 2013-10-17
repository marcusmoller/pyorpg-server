import sqlite3
import os.path
import pickle

from objects import *
from utils import *

import globalvars as g

database = None

def setupDatabase():
    global database
    database = Database(g.dataFolder + "/game_db.db")

class Database():
    def __init__(self, database):
        # check if database exists, if not, create it
        if os.path.isfile(database):
            g.serverLogger.info('Database has been found')
        else:
            g.serverLogger.info('No database has been found. Creating one...')
            self.createDatabase(database)
            return

        # connect to database
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def createDatabase(self, database_name):
        ''' if the database haven't been created, create it '''
        self.conn = sqlite3.connect(database_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # create table 'accounts'
        self.sendQuery("CREATE TABLE accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT);")

        # create table 'characters'
        self.sendQuery("CREATE TABLE characters (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                 account_id INTEGER, \
                                                 name TEXT, \
                                                 class INTEGER, \
                                                 sprite INTEGER, \
                                                 level INTEGER, \
                                                 exp INTEGER, \
                                                 access INTEGER, \
                                                 map INTEGER, \
                                                 x INTEGER, y INTEGER, \
                                                 direction INTEGER, \
                                                 helmet INTEGER, armor INTEGER, weapon INTEGER, shield INTEGER, \
                                                 stats_strength INTEGER, stats_defense INTEGER, stats_speed INTEGER, stats_magic INTEGER, \
                                                 vital_hp INTEGER, vital_mp INTEGER, vital_sp INTEGER);")

        # create table 'classes'
        self.sendQuery("CREATE TABLE classes (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                              name TEXT, \
                                              sprite INTEGER, \
                                              stat_strength INTEGER, stat_defense INTEGER, stat_speed INTEGER, stat_magic INTEGER);")

        # create table 'items'
        self.sendQuery("CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                              name TEXT, \
                                              pic INTEGER, \
                                              type INTEGER, \
                                              data1 INTEGER, data2 INTEGER, data3 INTEGER);")

        # create table 'spells'
        self.sendQuery("CREATE TABLE spells (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                              name TEXT, \
                                              pic INTEGER, \
                                              type INTEGER, \
                                              reqmp INTEGER, reqclass INTEGER, reqlevel INTEGER,\
                                              data1 INTEGER, data2 INTEGER, data3 INTEGER);")

        # create table 'inventory'
        self.sendQuery("CREATE TABLE inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                character_id INTEGER, \
                                                item_id INTEGER, \
                                                value INTEGER, \
                                                durability INTEGER);")

        # create table 'spellbook'
        self.sendQuery("CREATE TABLE spellbook (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                character_id INTEGER, \
                                                spellnum INTEGER);")

        # create table 'npcs'
        self.sendQuery("CREATE TABLE npcs (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                 name TEXT, \
                                                 sprite INTEGER, \
                                                 attack_say TEXT, \
                                                 spawn_secs INTEGER, \
                                                 behavior INTEGER, \
                                                 range INTEGER, \
                                                 drop_chance INTEGER, drop_item INTEGER, drop_item_value INTEGER,  \
                                                 stat_strength INTEGER, stat_defense INTEGER, stat_speed INTEGER, stat_magic INTEGER);")


        # insert sample account 'admin'
        self.sendQuery("INSERT INTO accounts (username, password) VALUES ('admin', 'admin');")

        # insert sample character 'Admin'
        self.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction, stats_strength, stats_defense, stats_speed, stats_magic, vital_hp, vital_mp, vital_sp) VALUES (1, 'Admin', 1, 1, 1, 0, 4, 1, 7, 5, 0, 2, 3, 7, 8, 4, 7, 3);")

        # insert sample classes "Warrior" and "Mage"
        self.sendQuery("INSERT INTO classes (name, sprite, stat_strength, stat_defense, stat_speed, stat_magic) VALUES ('Warrior', 0, 7, 5, 4, 2);")
        self.sendQuery("INSERT INTO classes (name, sprite, stat_strength, stat_defense, stat_speed, stat_magic) VALUES ('Mage', 1, 2, 3, 7, 8);")

        # insert sample item "gold" and "Noob Helmet"
        self.sendQuery("INSERT INTO items (name, pic, type, data1, data2, data3) VALUES ('Gold', 3, 12, 0, 0, 0);")
        self.sendQuery("INSERT INTO items (name, pic, type, data1, data2, data3) VALUES ('Helmet of the Noob', 0, 3, 5, 7, 0);")

        # insert sample spell 'Enflame'
        self.sendQuery("INSERT INTO spells (name, pic, type, reqmp, reqclass, reqlevel, data1, data2, data3) VALUES ('Enflame', 0, 3, 4, null, 1, 4, 0, 0);")

        # add item "Noob Helmet" to character 'Admin'
        self.sendQuery("INSERT INTO inventory (character_id, item_id, value, durability) VALUES (1, 2, 1, 25);")

        # add spell 'Enflame' to character 'Admin'
        self.sendQuery("INSERT INTO spellbook (character_id, spellnum) VALUES (1, 1);")

        self.saveChanges()
        g.serverLogger.info('Database has been created!')

    def sendQuery(self, query, *args):
        try:
            return self.cursor.execute(query, *args)
        except sqlite3.Error, msg:
            print msg

    def saveChanges(self):
        self.conn.commit()

    def closeDatabase(self):
        self.conn.close()

    def getNumberOfRows(self, tableName):
        ''' gets the number of rows in a table
            uses sql function  "SELECT COUNT(*) FROM tableName; '''
        result = self.sendQuery("SELECT COUNT(*) FROM " + tableName + ";")
        return result.fetchone()[0]


############
# ACCOUNTS #
############
def accountExists(name):
    query = database.sendQuery("SELECT * FROM accounts WHERE username='%s';" % name)
    rows = query.fetchone()

    if not rows:
        return False

    else:
        return True

def passwordOK(name, password):
    if accountExists(name):
        query = database.sendQuery("SELECT * FROM accounts WHERE username='%s';" % name)
        rows = query.fetchone()

        if password == rows[2]:
            return True

def addAccount(index, name, password):
    Player[index].Login = name
    Player[index].Password = password

    for i in range(MAX_CHARS):
        clearChar(index, i)
        # add 3


    saveAccount(name, password)
    savePlayer(index)

def deleteName(name):
    print "todo"

##############
# CHARACTERS #
##############

def charExist(index, charNum):
    if len(Player[index].char[charNum].name) > 0:
        return True

def addChar(index, name, sex, classNum, charNum):
    if len(Player[index].char[charNum].name) == 0:
        print "addChar() init"
        TempPlayer[index].charNum = charNum

        Player[index].char[charNum].name = name
        Player[index].char[charNum].sex = sex
        Player[index].char[charNum].Class = classNum

        # todo, add sex?
        Player[index].char[charNum].sprite = Class[classNum].sprite

        Player[index].char[charNum].level = 1
        Player[index].char[charNum].exp = 0

        for n in range(Stats.stat_count):
            Player[index].char[charNum].stats[n] = Class[classNum].stat[n]

        Player[index].char[charNum].vitals[Vitals.hp] = getPlayerMaxVital(index, Vitals.hp)
        Player[index].char[charNum].vitals[Vitals.mp] = getPlayerMaxVital(index, Vitals.mp)
        Player[index].char[charNum].vitals[Vitals.sp] = getPlayerMaxVital(index, Vitals.sp)

        Player[index].char[charNum].map = START_MAP
        Player[index].char[charNum].x = START_X
        Player[index].char[charNum].y = START_Y

        savePlayer(index)

def saveChar(index):
    print "todo"


def delChar(index, charNum):
    #deleteName
    clearChar(index, charNum)
    savePlayer(index)

def findChar(name):
    query = database.sendQuery("SELECT * FROM characters WHERE name='%s';" % name)
    rows = query.fetchone()

    if rows == None:
        return False

    else:
        return True

###########
# PLAYERS #
###########
def saveAccount(name, password):
    query = database.sendQuery("INSERT INTO accounts (username, password) VALUES ('%s', '%s');" % (name, password))
    database.saveChanges()

def savePlayer(index):
    # check if character/player already exists
    query = database.sendQuery("SELECT * FROM characters WHERE name='%s';" % getPlayerName(index))
    rows = query.fetchone()

    if rows == None:
        # character/player doesnt exist, create it

        # get account id
        query = database.sendQuery("SELECT id FROM accounts WHERE username='%s';" % getPlayerLogin(index))
        result = query.fetchone()
        accountID = result['id']

        # save character
        query = database.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction, helmet, armor, weapon, shield, stats_strength, stats_defense, stats_speed, stats_magic, vital_hp, vital_mp, vital_sp) \
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", \
                                                             (accountID,                \
                                                              getPlayerName(index),     \
                                                              getPlayerClass(index),    \
                                                              getPlayerSprite(index),   \
                                                              getPlayerLevel(index),    \
                                                              getPlayerExp(index),      \
                                                              getPlayerAccess(index),   \
                                                              getPlayerMap(index),      \
                                                              getPlayerX(index),        \
                                                              getPlayerY(index),        \
                                                              getPlayerDir(index),      \
                                                              getPlayerEquipmentSlot(index, Equipment.helmet), \
                                                              getPlayerEquipmentSlot(index, Equipment.armor), \
                                                              getPlayerEquipmentSlot(index, Equipment.weapon), \
                                                              getPlayerEquipmentSlot(index, Equipment.shield), \
                                                              getPlayerStat(index, Stats.strength),  \
                                                              getPlayerStat(index, Stats.defense),  \
                                                              getPlayerStat(index, Stats.speed),  \
                                                              getPlayerStat(index, Stats.magic),  \
                                                              getPlayerVital(index, Vitals.hp), \
                                                              getPlayerVital(index, Vitals.mp), \
                                                              getPlayerVital(index, Vitals.sp)))

    elif len(rows) > 0:
        # character/player exists, so update the character
        charId = rows['id']

        query = database.sendQuery("""UPDATE characters SET sprite=?,
                                                          level=?,
                                                          exp=?,
                                                          map=?,
                                                          x=?,
                                                          y=?,
                                                          access=?,
                                                          direction=?,
                                                          helmet=?, armor=?, weapon=?, shield=?,
                                                          stats_strength=?, stats_defense=?, stats_speed=?, stats_magic=?,
                                                          vital_hp=?, vital_mp=?, vital_sp=?
                                                          WHERE name=?;""", (getPlayerSprite(index),     \
                                                                               getPlayerLevel(index),    \
                                                                               getPlayerExp(index),      \
                                                                               getPlayerMap(index),      \
                                                                               getPlayerX(index),        \
                                                                               getPlayerY(index),        \
                                                                               getPlayerAccess(index),   \
                                                                               getPlayerDir(index),      \
                                                                               getPlayerEquipmentSlot(index, Equipment.helmet), \
                                                                               getPlayerEquipmentSlot(index, Equipment.armor), \
                                                                               getPlayerEquipmentSlot(index, Equipment.weapon), \
                                                                               getPlayerEquipmentSlot(index, Equipment.shield), \
                                                                               getPlayerStat(index, Stats.strength),  \
                                                                               getPlayerStat(index, Stats.defense),  \
                                                                               getPlayerStat(index, Stats.speed),  \
                                                                               getPlayerStat(index, Stats.magic),  \
                                                                               getPlayerVital(index, Vitals.hp), \
                                                                               getPlayerVital(index, Vitals.mp), \
                                                                               getPlayerVital(index, Vitals.sp), \
                                                                               getPlayerName(index)))

        # save inventory
        for i in range(MAX_INV):
            if getPlayerInvItemNum(index, i) != None:
                # add item to inventory if its not already there
                itemNum = getPlayerInvItemNum(index, i)

                # check if its already there
                invQuery = database.sendQuery("SELECT * FROM inventory WHERE (character_id=%i AND item_id=%i);" % (charId, (itemNum+1)))
                invRows = query.fetchone()

                if invRows == None:
                    # doesnt exist so add item
                    invQuery = database.sendQuery('INSERT INTO inventory (character_id, item_id, value, durability) \
                                                               VALUES (%i, %i, %i, %i);' \
                                                               % (charId, \
                                                                  (getPlayerInvItemNum(index, i)+1),
                                                                  getPlayerInvItemValue(index, i),
                                                                  getPlayerInvItemDur(index, i)))

                elif len(invRows) > 0:
                    # item has already been added, update value and durability
                    # get id
                    rowId = invRows['id']
                    invQuery = database.sendQuery('UPDATE inventory SET value=%i, durability=%i WHERE id=%i;' % (getPlayerInvItemValue(index, i), getPlayerInvItemDur(index, i), rowId))

        for i in range(MAX_PLAYER_SPELLS):
            if getPlayerSpell(index, i) is not None:
                spellNum = getPlayerSpell(index, i)

                # check if its already there
                spbQuery = database.sendQuery("SELECT * FROM spellbook WHERE (character_id=%i AND spellnum=%i);" % (charId, (spellNum+1)))
                spbRows = query.fetchone()

                if spbRows is None:
                    # doesnt exist, so add the spell
                    spbQuery = database.sendQuery('INSERT INTO spellbook (character_id, spellnum) \
                                                               VALUES (?, ?);', \
                                                                 (charId, \
                                                                 spellNum+1))

                elif len(spbRows) > 0:
                    # item is already there, so do nothing
                    continue

    database.saveChanges()

''' Load account details from database '''
def loadPlayer(index, name):
    clearPlayer(index)

    # fetch account details
    query = database.sendQuery("SELECT * FROM accounts WHERE username='%s';" % name)
    rows = query.fetchone()

    accountID = rows['id']
    Player[index].Login = rows['username']
    Player[index].Password = rows['password']

    # fetch character details
    query = database.sendQuery("SELECT * FROM characters WHERE account_id=%i;" % accountID)
    rows = query.fetchall()

    for i in range(0, MAX_CHARS):
        try:
            Player[index].char[i].name = rows[i]['name']
            Player[index].char[i].Class = rows[i]['class']
            Player[index].char[i].access = rows[i]['access']
            Player[index].char[i].sprite = rows[i]['sprite']
            Player[index].char[i].level = rows[i]['level']
            Player[index].char[i].exp = rows[i]['exp']
            Player[index].char[i].Map = rows[i]['map']
            Player[index].char[i].x = rows[i]['x']
            Player[index].char[i].y = rows[i]['y']
            Player[index].char[i].direction = rows[i]['direction']

            # set stats
            Player[index].char[i].stats[Stats.strength] = rows[i]['stats_strength']
            Player[index].char[i].stats[Stats.defense] = rows[i]['stats_defense']
            Player[index].char[i].stats[Stats.speed] = rows[i]['stats_speed']
            Player[index].char[i].stats[Stats.magic] = rows[i]['stats_magic']

            # set vitals
            Player[index].char[i].vitals[Vitals.hp] = rows[i]['vital_hp']
            Player[index].char[i].vitals[Vitals.mp] = rows[i]['vital_mp']
            Player[index].char[i].vitals[Vitals.sp] = rows[i]['vital_sp']

            # load equipment
            Player[index].char[i].equipment[Equipment.helmet] = rows[i]['helmet']
            Player[index].char[i].equipment[Equipment.armor] = rows[i]['armor']
            Player[index].char[i].equipment[Equipment.weapon] = rows[i]['weapon']
            Player[index].char[i].equipment[Equipment.shield] = rows[i]['shield']

            # load inventory
            charId = rows[i][0]

            invQuery = database.sendQuery("SELECT * FROM inventory WHERE character_id=%i;" % charId)
            invRow = invQuery.fetchall()

            for j in range(len(invRow)):
                try:
                    Player[index].char[i].inv[j].num = invRow[j]['item_id']-1
                    Player[index].char[i].inv[j].value = invRow[j]['value']
                    Player[index].char[i].inv[j].dur = invRow[j]['durability']

                except:
                    break

            # load spellbook
            spbQuery = database.sendQuery("SELECT * FROM spellbook WHERE character_id=%i;" % charId)
            spbRow = spbQuery.fetchall()

            for k in range(len(spbRow)):
                try:
                    setPlayerSpell(index, k, spbRow[k]['spellnum']-1)

                except:
                    break

        except:
            break


def clearPlayer(index):
    ''' resets the given index of Player array '''
    Player[index] = AccountClass()


def clearChar(index, charNum):
    ''' resets the given index of the character array '''
    Player[index].char[charNum] = PlayerClass()

###########
# CLASSES #
###########

def createClasses():
    # not necassary?
    maxClasses = 2

def loadClasses():
    # get max classes
    g.maxClasses = database.getNumberOfRows("classes")

    for i in range(0, g.maxClasses):
        query = database.sendQuery("SELECT * FROM classes WHERE id=%i;" % (i+1))
        rows = query.fetchone()

        Class[i].name = rows['name']
        Class[i].sprite = rows['sprite']
        Class[i].stat[Stats.strength] = int(rows['stat_strength'])
        Class[i].stat[Stats.defense] = int(rows['stat_defense'])
        Class[i].stat[Stats.speed] = int(rows['stat_speed'])
        Class[i].stat[Stats.magic] = int(rows['stat_magic'])

def saveClasses():
    # todo
    print "todo"

def clearClasses():
    for i in range(g.maxClasses):
        Class[i] = ClassClass()

def getClassName(classNum):
    return Class[classNum].name

def getClassMaxVital(classNum, vital):
    if vital == Vitals.hp:
        return (1 + (Class[classNum].stat[Stats.strength] // 2) + Class[classNum].stat[Stats.strength]) * 2
    elif vital == Vitals.mp:
        return (1 + (Class[classNum].stat[Stats.magic] // 2) + Class[classNum].stat[Stats.magic]) * 2
    elif vital == Vitals.sp:
        return (1 + (Class[classNum].stat[Stats.speed] // 2) + Class[classNum].stat[Stats.speed]) * 2

def getClassStat(classNum, stat):
    return Class[i].Stat[stat]

#########
# ITEMS #
#########

def saveItems():
    for i in range(MAX_ITEMS):
        if Item[i].name != '':
            saveItem(i)


def saveItem(itemNum):
    # todo: rework the id part

    # check if item already exists
    query = database.sendQuery("SELECT * FROM items WHERE id=%i;" % (itemNum+1))
    rows = query.fetchone()

    if rows == None:
        # item doesnt exist, create it
        query = database.sendQuery("INSERT INTO items (id, name, pic, type, data1, data2, data3) \
                                                           VALUES (%i, '%s', %i, %i, %i, %i, %i);" \
                                                           % (int(itemNum+1),             \
                                                              Item[itemNum].name,  \
                                                              Item[itemNum].pic,   \
                                                              Item[itemNum].type,  \
                                                              Item[itemNum].data1, \
                                                              Item[itemNum].data2, \
                                                              Item[itemNum].data3))

    elif len(rows) > 0:
        # item already exists, so update the item
        query = database.sendQuery("UPDATE items SET name='%s', \
                                                          pic=%i, \
                                                          type=%i, \
                                                          data1=%i, \
                                                          data2=%i, \
                                                          data3=%i \
                                                          WHERE id=%i;" % (Item[itemNum].name,  \
                                                                           Item[itemNum].pic,   \
                                                                           Item[itemNum].type,  \
                                                                           Item[itemNum].data1, \
                                                                           Item[itemNum].data2, \
                                                                           Item[itemNum].data3, \
                                                                           int(itemNum+1)))

    database.saveChanges()


def loadItems():
    #checkItems()
    # get max classes
    itemAmount = database.getNumberOfRows('items')

    for i in range(0, itemAmount):
        query = database.sendQuery("SELECT * FROM items WHERE id=%i;" % (i+1))
        rows = query.fetchone()

        Item[i].name = rows['name']
        Item[i].pic = int(rows['pic'])
        Item[i].type = int(rows['type'])
        Item[i].data1 = rows['data1']
        Item[i].data2 = rows['data2']
        Item[i].data3 = rows['data3']


def checkItems():
    for i in range(MAX_ITEMS):
        print "probably not necassary"


# Spells
def saveSpell(spellNum):
    # todo: rework the id part

    # check if spell already exists
    query = database.sendQuery("SELECT * FROM spells WHERE id=%i;" % (spellNum+1))
    rows = query.fetchone()

    if rows == None:
        # spell doesnt exist, create it
        query = database.sendQuery("INSERT INTO spells (id, name, pic, type, reqmp, reqclass, reqlevel, data1, data2, data3) \
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", \
                                                             (int(spellNum+1), \
                                                              Spell[spellNum].name,  \
                                                              Spell[spellNum].pic,   \
                                                              Spell[spellNum].type,  \
                                                              Spell[spellNum].reqMp, \
                                                              Spell[spellNum].reqClass, \
                                                              Spell[spellNum].reqLevel, \
                                                              Spell[spellNum].data1, \
                                                              Spell[spellNum].data2, \
                                                              Spell[spellNum].data3))

    elif len(rows) > 0:
        # spell already exists, so update the spell
        query = database.sendQuery("UPDATE spells SET name=?, \
                                                          pic=?, \
                                                          type=?, \
                                                          reqmp=?, \
                                                          reqclass=?, \
                                                          reqlevel=?, \
                                                          data1=?, \
                                                          data2=?, \
                                                          data3=? \
                                                          WHERE id=?;", (Spell[spellNum].name,  \
                                                                           Spell[spellNum].pic,   \
                                                                           Spell[spellNum].type,  \
                                                                           Spell[spellNum].reqMp, \
                                                                           Spell[spellNum].reqClass, \
                                                                           Spell[spellNum].reqLevel, \
                                                                           Spell[spellNum].data1, \
                                                                           Spell[spellNum].data2, \
                                                                           Spell[spellNum].data3, \
                                                                           int(spellNum+1)))

    database.saveChanges()

def saveSpells():
    print 'Saving spells...'
    for i in range(MAX_SPELLS):
        saveSpell(i)

def loadSpells():
    #checkItems()
    # get max classes
    spellAmount = database.getNumberOfRows('spells')

    for i in range(0, spellAmount):
        query = database.sendQuery("SELECT * FROM spells WHERE id=%i;" % (i+1))
        rows = query.fetchone()

        Spell[i].name = rows['name']
        Spell[i].pic = rows['pic']
        Spell[i].type = rows['type']

        Spell[i].reqMp = rows['reqmp']
        Spell[i].reqClass = rows['reqclass']
        Spell[i].reqLevel = rows['reqlevel']

        Spell[i].data1 = rows['data1']
        Spell[i].data2 = rows['data2']
        Spell[i].data3 = rows['data3']

def clearSpell(index):
    Spell[index] = SpellClass()

def clearSpells():
    for i in range(MAX_SPELLS):
        Spell[i] = SpellClass()

# NPC

def saveNpc(npcNum):
    # todo: rework the id part

    # check if npc already exists
    query = database.sendQuery("SELECT * FROM npcs WHERE id=%i;" % (npcNum+1))
    rows = query.fetchone()

    if rows == None:
        # npc doesnt exist, create it
        query = database.sendQuery("INSERT INTO npcs (id, name, sprite, attack_say, spawn_secs, behavior, range, drop_chance, drop_item, drop_item_value, stat_strength, stat_defense, stat_magic, stat_speed) \
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", \
                                                                (int(npcNum+1), \
                                                                NPC[npcNum].name,  \
                                                                NPC[npcNum].sprite,   \
                                                                NPC[npcNum].attackSay,  \
                                                                NPC[npcNum].spawnSecs, \
                                                                NPC[npcNum].behaviour, \
                                                                NPC[npcNum].range, \
                                                                NPC[npcNum].dropChance, \
                                                                NPC[npcNum].dropItem, \
                                                                NPC[npcNum].dropItemValue, \
                                                                NPC[npcNum].stat[Stats.strength], \
                                                                NPC[npcNum].stat[Stats.defense], \
                                                                NPC[npcNum].stat[Stats.magic], \
                                                                NPC[npcNum].stat[Stats.speed]))

    elif len(rows) > 0:
        # npc already exists, so update the npc
        query = database.sendQuery("UPDATE npcs SET name=?, \
                                                          sprite=?, \
                                                          attack_say=?, \
                                                          spawn_secs=?, \
                                                          behavior=?, \
                                                          range=?, \
                                                          drop_chance=?, \
                                                          drop_item=?, \
                                                          drop_item_value=?, \
                                                          stat_strength=?, \
                                                          stat_defense=?, \
                                                          stat_magic=?, \
                                                          stat_speed=? \
                                                          WHERE id=?;", (NPC[npcNum].name,  \
                                                                           NPC[npcNum].sprite,   \
                                                                           NPC[npcNum].attackSay,  \
                                                                           NPC[npcNum].spawnSecs, \
                                                                           NPC[npcNum].behaviour, \
                                                                           NPC[npcNum].range, \
                                                                           NPC[npcNum].dropChance, \
                                                                           NPC[npcNum].dropItem, \
                                                                           NPC[npcNum].dropItemValue, \
                                                                           NPC[npcNum].stat[Stats.strength], \
                                                                           NPC[npcNum].stat[Stats.defense], \
                                                                           NPC[npcNum].stat[Stats.magic], \
                                                                           NPC[npcNum].stat[Stats.speed], \
                                                                           int(npcNum+1)))

    database.saveChanges()

def saveNpcs():
    for i in range(MAX_NPCS):
        saveNpcs(i)


def loadNpcs():
    npcAmount = database.getNumberOfRows('npcs')

    for i in range(0, npcAmount):
        query = database.sendQuery("SELECT * FROM npcs WHERE id=%i;" % (i+1))
        rows = query.fetchone()

        NPC[i].name = rows['name']
        NPC[i].attackSay = rows['attack_say']
        NPC[i].sprite = int(rows['sprite'])
        NPC[i].spawnSecs = int(rows['spawn_secs'])
        NPC[i].behaviour = int(rows['behavior'])
        NPC[i].range = int(rows['range'])

        NPC[i].dropChance = int(rows['drop_chance'])
        NPC[i].dropItem = rows['drop_item']
        NPC[i].dropItemValue = int(rows['drop_item_value'])

        NPC[i].stat[Stats.strength] = int(rows['stat_strength'])
        NPC[i].stat[Stats.defense] = int(rows['stat_defense'])
        NPC[i].stat[Stats.magic] = int(rows['stat_magic'])
        NPC[i].stat[Stats.speed] = int(rows['stat_speed'])


#################
# MAP FUNCTIONS #
#################

def saveMap(mapNum):
    pickle.dump(Map[mapNum], open(g.dataFolder + "/maps/" + str(mapNum) + ".pom", 'wb'))

def saveMaps():
    for i in range(MAX_MAPS):
        saveMap(i)

def loadMaps():
    checkMaps()

    for i in range(MAX_MAPS):
        Map[i] = pickle.load(open(g.dataFolder + "/maps/" + str(i) + ".pom", 'rb'))

def checkMaps():
    for i in range(MAX_MAPS):
        if not os.path.isfile(g.dataFolder + "/maps/" + str(i) + ".pom"):
            saveMap(i)


def clearMapItem(index, mapNum):
    mapItem[mapNum][index] = MapItemClass()

def clearMapItems():
    for i in range(MAX_MAPS):
        for j in range(MAX_MAP_ITEMS):
            clearMapItem(j, i)

def clearMapNpc(index, mapNum):
    mapNPC[mapNum][index] = MapNPCClass()

def clearMapNpcs():
    for i in range(MAX_MAPS):
        for j in range(MAX_MAP_NPCS):
            clearMapNpc(j, i)

def clearMap(mapNum):
    Map[mapNum].tileSet = 1
    Map[mapNum].name = ""
    playersOnMap[mapNum] = 0
    MapCache[mapNum] = ""

def clearMaps():
    for i in range(MAX_MAPS):
        clearMap(i)

####################
# PLAYER FUNCTIONS #
####################

''' Player login name '''
def getPlayerLogin(index):
    return Player[index].Login


''' Player name '''
def getPlayerName(index):
    return Player[index].char[TempPlayer[index].charNum].name

def setPlayerName(index, name):
    Player[index].char[TempPlayer[index].charNum].name = name

''' player class '''
def getPlayerClass(index):
    return Player[index].char[TempPlayer[index].charNum].Class

def setPlayerClass(index, classNum):
    Player[index].char[TempPlayer[index].charNum].Class = classNum


''' Player sprite '''
def getPlayerSprite(index):
    return Player[index].char[TempPlayer[index].charNum].sprite

def setPlayerSprite(index, sprite):
    Player[index].char[TempPlayer[index].charNum].sprite = sprite


''' player level '''
def getPlayerLevel(index):
    return Player[index].char[TempPlayer[index].charNum].level

def setPlayerLevel(index, level):
    Player[index].char[TempPlayer[index].charNum].level = level

''' player next level '''
def getPlayerNextLevel(index):
    return (getPlayerLevel(index) + 1) * (getPlayerStat(index, Stats.strength) + getPlayerStat(index, Stats.defense) + getPlayerStat(index, Stats.magic) + getPlayerStat(index, Stats.speed) + getPlayerPoints(index)) * 25

''' player exp '''
def getPlayerExp(index):
    return Player[index].char[TempPlayer[index].charNum].exp

def setPlayerExp(index, exp):
    Player[index].char[TempPlayer[index].charNum].exp = exp

''' player access '''
def getPlayerAccess(index):
    return Player[index].char[TempPlayer[index].charNum].access

def setPlayerAccess(index, access):
    Player[index].char[TempPlayer[index].charNum].access = access

''' player vital '''
def getPlayerVital(index, vital):
    return Player[index].char[TempPlayer[index].charNum].vitals[vital]

def setPlayerVital(index, vital, value):
    Player[index].char[TempPlayer[index].charNum].vitals[vital] = value

    if getPlayerVital(index, vital) > getPlayerMaxVital(index, vital):
        Player[index].char[TempPlayer[index].charNum].vitals[vital] = getPlayerMaxVital(index, vital)

    if getPlayerVital(index, vital) < 0:
        Player[index].char[TempPlayer[index].charNum].vitals[vital] = 0

''' player max vital '''
def getPlayerMaxVital(index, vital):
    charNum = TempPlayer[index].charNum

    if vital == Vitals.hp:
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.strength) // 2) + Class[Player[index].char[charNum].Class].stat[Stats.strength] * 2)
    elif vital == Vitals.mp:
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.magic) // 2) + Class[Player[index].char[charNum].Class].stat[Stats.magic] * 2)
    elif vital == Vitals.sp:
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.speed) // 2) + Class[Player[index].char[charNum].Class].stat[Stats.speed] * 2)

''' player stats '''
def getPlayerStat(index, stat):
    return Player[index].char[TempPlayer[index].charNum].stats[stat]

def setPlayerStat(index, stat, value):
    Player[index].char[TempPlayer[index].charNum].stats[stat] = value


''' player stats points '''
def getPlayerPoints(index):
    return Player[index].char[TempPlayer[index].charNum].statsPoints

def setPlayerPoints(index, points):
    Player[index].char[TempPlayer[index].charNum].statsPoints = points


''' Player map '''
def getPlayerMap(index):
    return Player[index].char[TempPlayer[index].charNum].Map

def setPlayerMap(index, mapNum):
    Player[index].char[TempPlayer[index].charNum].Map = mapNum


''' Player x '''
def getPlayerX(index):
    return Player[index].char[TempPlayer[index].charNum].x

def setPlayerX(index, x):
    Player[index].char[TempPlayer[index].charNum].x = x


''' Player y '''
def getPlayerY(index):
    return Player[index].char[TempPlayer[index].charNum].y

def setPlayerY(index, y):
    Player[index].char[TempPlayer[index].charNum].y = y


''' Player direction '''
def getPlayerDir(index):
    return Player[index].char[TempPlayer[index].charNum].Dir

def setPlayerDir(index, direction):
    Player[index].char[TempPlayer[index].charNum].Dir = direction

''' Player inventory '''
def getPlayerInvItemNum(index, invSlot):
    return Player[index].char[TempPlayer[index].charNum].inv[invSlot].num
def setPlayerInvItemNum(index, invSlot, itemNum):
    Player[index].char[TempPlayer[index].charNum].inv[invSlot].num = itemNum

def getPlayerInvItemValue(index, invSlot):
    return Player[index].char[TempPlayer[index].charNum].inv[invSlot].value
def setPlayerInvItemValue(index, invSlot, itemValue):
    Player[index].char[TempPlayer[index].charNum].inv[invSlot].value = itemValue

def getPlayerInvItemDur(index, invSlot):
    return Player[index].char[TempPlayer[index].charNum].inv[invSlot].dur
def setPlayerInvItemDur(index, invSlot, itemDur):
    Player[index].char[TempPlayer[index].charNum].inv[invSlot].dur = itemDur

''' player spell '''
def getPlayerSpell(index, spellSlot):
    return Player[index].char[TempPlayer[index].charNum].spell[spellSlot]
def setPlayerSpell(index, spellSlot, spellNum):
    Player[index].char[TempPlayer[index].charNum].spell[spellSlot] = spellNum

''' player equipment '''
def getPlayerEquipmentSlot(index, equipmentSlot):
    return Player[index].char[TempPlayer[index].charNum].equipment[equipmentSlot]
def setPlayerEquipmentSlot(index, invNum, equipmentSlot):
    Player[index].char[TempPlayer[index].charNum].equipment[equipmentSlot] = invNum
