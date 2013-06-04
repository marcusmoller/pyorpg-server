import sqlite3
import os.path
import pickle

from objects import *
from utils import *

import globalvars as g

class Database():
	def __init__(self, database):
		# check if database exists, if not, create it
		if os.path.isfile(database):
			log('Database has been found')
		else:
			log('No database has been found. Creating one...')
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
		
		# insert sample account 'admin'
		self.sendQuery("INSERT INTO accounts (username, password) VALUES ('admin', 'admin');")

		# insert sample character 'Admin'
		self.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction) VALUES (1, 'Admin', 0, 1, 1, 0, 4, 1, 7, 5, 0);")

		# insert sample class "Warrior"
		self.sendQuery("INSERT INTO classes (name, sprite, stat_strength, stat_defense, stat_speed, stat_magic) VALUES ('Warrior', 1, 7, 5, 4, 2);")

		self.saveChanges()
		log('Database has been created!')


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

database = Database(g.dataFolder + "/game_db.db")


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
		print "new character"

		# get account id
		query = database.sendQuery("SELECT id FROM accounts WHERE username='%s';" % getPlayerLogin(index))
		result = query.fetchone()
		accountID = result[0]

		# save character
		query = database.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction, stats_strength, stats_defense, stats_speed, stats_magic, vital_hp, vital_mp, vital_sp) \
			                        VALUES (%i, '%s', 0, 1, 1, 0, 0, 1, 1, 1, 0, 5, 5, 5, 5, 10, 10, 10)" \
			                        % (accountID, getPlayerName(index)))

		# todo: fix this
		'''query = database.sendQuery("INSERT INTO characters (account_id, name, class, sprite, level, exp, access, map, x, y, direction, stats_strength, stats_defense, stats_speed, stats_magic, vital_hp, vital_mp, vital_sp) \
								                           VALUES (%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);" \
								                           % (accountID,                \
								                           	  getPlayerName(index),     \
								                           	  Player[index].char[TempPlayer[index].charNum].Class, \
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
								                           	  getPlayerVital(index, 2)))'''

	elif len(rows) > 0:
		# character/player exists, so update the character
		query = database.sendQuery("UPDATE characters SET map=%i, \
			                                              x=%i, \
		                                                  y=%i, \
		                                                  direction=%i, \
		                                                  stats_strength=%i, stats_defense=%i, stats_speed=%i, stats_magic=%i, \
		                                                  vital_hp=%i, vital_mp=%i, vital_sp=%i \
		                                                  WHERE name='%s';" % (getPlayerMap(index),      \
		                                                  	                   getPlayerX(index),        \
		                                                  	                   getPlayerY(index),        \
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
	print rows

	for i in range(0, MAX_CHARS):
		try:
			Player[index].char[i].name = rows[i][2]
			Player[index].char[i].access = rows[i][7]
			Player[index].char[i].sprite = rows[i][4]
			Player[index].char[i].Map = rows[i][8]
			Player[index].char[i].x = rows[i][9]
			Player[index].char[i].y = rows[i][10]
			Player[index].char[i].direction = rows[i][11]

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
		Class[i].sprite = rows[2] #todo, sprite shouldnt be here
		Class[i].stat[Stats.strength] = int(rows[3])
		Class[i].stat[Stats.defense] = int(rows[4])
		Class[i].stat[Stats.speed] = int(rows[5])
		Class[i].stat[Stats.magic] = int(rows[6])

		print Class[i].stat[Stats.magic]

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


''' Player direction '''
def getPlayerDir(index):
	return Player[index].char[TempPlayer[index].charNum].Dir

def setPlayerDir(index, direction):
	Player[index].char[TempPlayer[index].charNum].Dir = direction


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