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
        self.cursor = self.conn.cursor()


    def createDatabase(self, database_name):
        ''' if the database haven't been created, create it '''
        self.conn = sqlite3.connect(database_name)
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

        # create table 'inventory'
        self.sendQuery("CREATE TABLE inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                              character_id TEXT, \
                                              item_id INTEGER, \
                                              value INTEGER, \
                                              durability INTEGER);")

        # insert sample account 'admin'
        self.sendQuery("INSERT INTO accounts (username, password) VALUES ('admin', 'admin');")

        # insert sample character 'Admin'
        self.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction) VALUES (1, 'Admin', 0, 1, 1, 0, 4, 1, 7, 5, 0);")

        # insert sample classes "Warrior" and "Mage"
        self.sendQuery("INSERT INTO classes (name, sprite, stat_strength, stat_defense, stat_speed, stat_magic) VALUES ('Warrior', 0, 7, 5, 4, 2);")
        self.sendQuery("INSERT INTO classes (name, sprite, stat_strength, stat_defense, stat_speed, stat_magic) VALUES ('Mage', 1, 2, 3, 7, 8);")

        # insert sample item "gold" and "Noob Helmet"
        self.sendQuery("INSERT INTO items (name, pic, type, data1, data2, data3) VALUES ('Gold', 3, 12, 0, 0, 0);")
        self.sendQuery("INSERT INTO items (name, pic, type, data1, data2, data3) VALUES ('Helmet of the Noob', 16, 3, 5, 7, 0);")

        # add item "Noob Helmet" to character 'Admin'
        self.sendQuery("INSERT INTO inventory (character_id, item_id, value, durability) VALUES (1, 2, 1, 25);")

        self.saveChanges()
        g.serverLogger.info('Database has been created!')

    def sendQuery(self, query):
        try:
            return self.cursor.execute(query)
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
        accountID = result[0]

        # save character
        query = database.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction, stats_strength, stats_defense, stats_speed, stats_magic, vital_hp, vital_mp, vital_sp) \
                                                           VALUES (%i, '%s', %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i);" \
                                                           % (accountID,                \
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
                                                              getPlayerStat(index, 0),  \
                                                              getPlayerStat(index, 1),  \
                                                              getPlayerStat(index, 2),  \
                                                              getPlayerStat(index, 3),  \
                                                              getPlayerVital(index, 0), \
                                                              getPlayerVital(index, 1), \
                                                              getPlayerVital(index, 2)))

    elif len(rows) > 0:
        # character/player exists, so update the character
        query = database.sendQuery("UPDATE characters SET sprite=%i, \
                                                          map=%i, \
                                                          x=%i, \
                                                          y=%i, \
                                                          access=%i, \
                                                          direction=%i, \
                                                          stats_strength=%i, stats_defense=%i, stats_speed=%i, stats_magic=%i, \
                                                          vital_hp=%i, vital_mp=%i, vital_sp=%i \
                                                          WHERE name='%s';" % (getPlayerSprite(index),   \
                                                                               getPlayerMap(index),      \
                                                                               getPlayerX(index),        \
                                                                               getPlayerY(index),        \
                                                                               getPlayerAccess(index),   \
                                                                               getPlayerDir(index),      \
                                                                               getPlayerStat(index, 0),  \
                                                                               getPlayerStat(index, 1),  \
                                                                               getPlayerStat(index, 2),  \
                                                                               getPlayerStat(index, 3),  \
                                                                               getPlayerVital(index, 0), \
                                                                               getPlayerVital(index, 1), \
                                                                               getPlayerVital(index, 2), \
                                                                               getPlayerName(index)))

    database.saveChanges()

''' Load account details from database '''
def loadPlayer(index, name):
    clearPlayer(index)

    # fetch account details
    query = database.sendQuery("SELECT * FROM accounts WHERE username='%s';" % name)
    rows = query.fetchone()

    accountID = rows[0]
    Player[index].Login = rows[1]
    Player[index].Password = rows[2]

    # fetch character details
    query = database.sendQuery("SELECT * FROM characters WHERE account_id=%i;" % accountID)
    rows = query.fetchall()

    for i in range(0, MAX_CHARS):
        try:
            Player[index].char[i].name = rows[i][2]
            Player[index].char[i].access = rows[i][7]
            Player[index].char[i].sprite = rows[i][4]
            Player[index].char[i].Map = rows[i][8]
            Player[index].char[i].x = rows[i][9]
            Player[index].char[i].y = rows[i][10]
            Player[index].char[i].direction = rows[i][11]

            # load inventory
            charId = rows[i][0]

            invQuery = database.sendQuery("SELECT * FROM inventory WHERE character_id=%i;" % charId)
            invRow = invQuery.fetchall()

            for j in range(len(invRow)):
                try:
                    Player[index].char[i].inv[j].num = invRow[j][2]-1
                    Player[index].char[i].inv[j].value = invRow[j][3]
                    Player[index].char[i].inv[j].dur = invRow[j][4]

                except:
                    break

        except:
            break

def clearPlayer(index):
    Player[index] = AccountClass()

def clearChar(index, charNum):
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

        Class[i].name = rows[1]
        Class[i].sprite = rows[2] # todo, sprite shouldnt be here
        Class[i].stat[Stats.strength] = int(rows[3])
        Class[i].stat[Stats.defense] = int(rows[4])
        Class[i].stat[Stats.speed] = int(rows[5])
        Class[i].stat[Stats.magic] = int(rows[6])

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

        Item[i].name = rows[1]
        Item[i].pic = int(rows[2])
        Item[i].type = int(rows[3])
        Item[i].data1 = rows[4]
        Item[i].data2 = rows[5]
        Item[i].data3 = rows[6]


def checkItems():
    for i in range(MAX_ITEMS):
        print "probably not necassary"


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
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.strength)/2)) # + smth
    elif vital == Vitals.mp:
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.magic)/2)) # + smth
    elif vital == Vitals.sp:
        return (Player[index].char[charNum].level + (getPlayerStat(index, Stats.speed)/2)) # + smth

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

def getPlayerEquipmentSlot(index, equipmentSlot):
    return "todo"
def setPlayerEquipmentSlot(index, invNum, equipmentSlot):
    print "todo"
