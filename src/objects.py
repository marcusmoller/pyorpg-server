from constants import *

# Public data structures
# - Initializations are at the bottom of the source code

class Stats():
    strength,  \
    defense,   \
    speed,     \
    magic,     \
    stat_count \
    = range(5)

class Vitals():
    hp,         \
    mp,         \
    sp,         \
    vital_count \
    = range(4)

class Equipment():
    weapon,         \
    armor,          \
    helmet,         \
    shield,         \
    equipment_count \
    = range(5)


class PlayerInvClass():
    def __init__(self):
        self.num = None
        self.value = 0
        self.dur = 0

class PlayerClass():
    def __init__(self):
        # General
        self.name = ""
        self.sex = 0
        self.Class = 1
        self.sprite = 0
        self.level = 1
        self.exp = 0
        self.access = 0
        self.pk = 0

        # stats
        self.stats = [None for i in range(Stats.stat_count)]
        self.stats[Stats.strength] = 0
        self.stats[Stats.defense] = 0
        self.stats[Stats.speed] = 0
        self.stats[Stats.magic] = 0
        self.statsPoints = 0

        # vitals (hp, mp etc.)
        self.vitals = [None for i in range(Vitals.vital_count)]
        self.vitals[Vitals.hp] = 0
        self.vitals[Vitals.mp] = 0
        self.vitals[Vitals.sp] = 0

        # equipment
        self.equipment = [None for i in range(Equipment.equipment_count)]

        # inventory
        self.inv = [PlayerInvClass() for i in range(MAX_INV)]

        # Position
        self.Map = 1    # None
        self.x = 5         # None
        self.y = 5         # None
        self.Dir = 1 # None

class AccountClass():
    def __init__(self):
        # Account
        self.Login = ""
        self.Password = None

        # Characters
        self.char = [PlayerClass() for i in range(10)]

class ClassClass():
    def __init__(self):
        self.name = ""
        self.sprite = 1
        self.stat = [None for i in range(Stats.stat_count)]


class TempPlayerClass():
    def __init__(self):
        # Non saved, local variables
        self.Buffer = None
        self.charNum = 0
        self.inGame = False

        self.attackTimer = 0
        self.target = 0

        self.dataTimer = None
        self.dataBytes = None
        self.dataPackets = None

        self.gettingMap = False


class TileClass():
    def __init__(self):
        self.ground = None
        self.mask = 0
        self.anim = 0
        self.fringe = None
        self.type = 0
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0

class MapClass():
    def __init__(self):
        self.name = ""
        self.revision = 0
        self.moral = None
        self.tileSet = 1

        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0

        self.bootMap = 0
        self.bootX = 0
        self.bootY = 0

        self.tile = [[TileClass() for i in range(MAX_MAPY)] for i in range(MAX_MAPX)]

class TempTileClass():
    def __init__(self):
        self.doorOpen = 0
        self.doorTime = 0

class MapItemClass():
    def __init__(self):
        self.num = None
        self.value = None
        self.dur = None

        self.x = None
        self.y = None

class ItemClass():
    def __init__(self):
        self.name = ""
        self.pic = 1
        self.type = 0
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0

class NPCClass():
    def __init__(self):
        self.name = ''
        self.attackSay = ''

        self.sprite = None
        self.spawnSecs = None
        self.behaviour = None
        self.range = None

        self.dropChance = None
        self.dropItem = None
        self.dropItemValue = None

        self.stat = [None for i in range(Stats.stat_count)]

class MapNPCClass():
    def __init__(self):
        self.num = None
        self.target = None

        self.vital = [None for i in range(Vitals.vital_count)]

        self.map = None
        self.x = None
        self.y = None
        self.dir = None

        # server use only
        self.spawnWait = None
        self.attackTimer = None


# Data initializations
Map = [MapClass() for i in range(MAX_MAPS)]
MapCache = [None] * MAX_MAPS
TempTile = [TempTileClass() for i in range(MAX_MAPS)]
playersOnMap = [None] * MAX_MAPS

Player = [AccountClass() for i in range(MAX_PLAYERS)]
TempPlayer = [TempPlayerClass() for i in range(MAX_PLAYERS)]

Class = [ClassClass() for i in range(99)]  # todo: dont use a fixed size, please
Item = [ItemClass() for i in range(MAX_ITEMS)]
NPC = [NPCClass() for i in range(MAX_NPCS)]
mapItem = [[MapItemClass() for i in range(MAX_MAP_ITEMS)] for j in range(MAX_MAPS)]
mapNPC = [[MapNPCClass() for i in range(MAX_MAP_NPCS)] for j in range(MAX_MAPS)]
