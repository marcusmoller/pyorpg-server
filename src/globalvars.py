import os

# online player variables
playersOnline = []
highIndex = 0
totalPlayersOnline = 0

# message of the day
MOTD = "Hello, world!"

# maximum classes
maxClasses = 0

# Protocol
conn = None

# folders
dataFolder = os.path.join('..', 'data')

# loggers
serverLogger = None
connectionLogger = None
