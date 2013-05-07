from database import *
from packettypes import *
from gamelogic import *
from objects import *
from constants import *
from utils import *

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

		elif packetType == ClientPackets.CSetSprite:
			self.handleSetSprite(index, jsonData)

		elif packetType == ClientPackets.CRequestNewMap:
			self.handleRequestNewMap(index, jsonData)

		elif packetType == ClientPackets.CMapData:
			self.handleMapData(index, jsonData)

		elif packetType == ClientPackets.CNeedMap:
			self.handleNeedMap(index, jsonData)

		elif packetType == ClientPackets.CRequestEditMap:
			self.handleRequestEditMap(index)

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
					# call AlertMsg(index, "Your name and password must be at least three characters in length.")
					return

				# check if account already exists
				if not accountExists(name):
					addAccount(index, name, password)
					log('Account ' + name + ' has been created')
					#alertmsg "Your account has been created!"
				else:
					log('Account name has already been taken!')
					#alertmsg "Sorry, that account name is already taken!"

	''' Player login '''
	def handleLogin(self, index, jsonData):
		if not isPlaying(index):
			if not isLoggedIn(index):
				plrName = jsonData[0]["name"]
				plrPassword = jsonData[0]["password"]

				# load the player
				loadPlayer(index, plrName)
				sendChars(index)

				log(getPlayerLogin(index) + ' has logged in')

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
			log("Character " + name + " added to " + getPlayerLogin(index) + "'s account.")
			# alertMsg(player created)



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

				log("Has began playing")

	''' say msg '''
	def handleSayMsg(self, index, jsonData):
		msg = jsonData[0]["msg"]
		log('player said something D:')
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
		print "handleNeedMap()"
		answer = jsonData[0]["answer"]

		if answer == 1:
			# needs new revision
			sendMap(index, getPlayerMap(index))

		sendJoinMap(index)
		TempPlayer[index].gettingMap = False
		sendMapDone(index)

	def handleRequestEditMap(self, index):
		if getPlayerAccess(index) < ADMIN_MAPPER:
			print "hacking attempt"
			return

		sendEditMap(index)


