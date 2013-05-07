SEP_CHAR = "-"
END_CHAR = "."

class ClientPackets:
	CPlayerMsg,  \
	CPlayerMove, \
	CPlayerDir,  \
	CQuit        \
	= range(4)

class ServerPackets:
	SPlayerMsg,  \
	SPlayerMove, \
	SPlayerDir   \
	= range(3)