"""
Implements a bot playing Four in a Row using a Tree Structure and a basic evaluation function
"""
import time
from functools import lru_cache

EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2


nodes_searched: int = 0
max_depth = 0
nodes_pruned = 0
width = 7
height = 6

def make_move(position, mask, col):
	new_position = position ^ mask
	new_mask = mask | (mask + (1 << (col*7)))
	return new_position, new_mask

def printBoard(board: list[list[int]]) -> None:
	for i in range(len(board)):
		print([board[i][j] +1 for j in range(width)])

def getBitBoard(starting_player: int, board: list[list[int]]) -> tuple[int, int]:
	position = 0
	mask = 0
	for i in range(height):
		for j in range(width):
			position += 1 << (j*width + height-i-1) if board_in[i][j] == starting_player else 0
			mask += 1 << (j*width + height-i-1) if board_in[i][j] != -1 else 0
	return (position, mask)

def getBoardFromBitstring(current_player: int, position: int, mask: int) -> list[list[int]]:
	board_out = [[-1 for j in range(width)] for i in range(height)]
	for i in range(height):
		for j in range(width):
			if(mask >> (j*7 + i) & 1 == 1):
				board_out[height-i-1][j] = current_player if (position >> (j*7 + i) & 1) else (1- current_player)
	return board_out

"""
Game isn't over when played
"""
def evaluationRoot(starting_player: int, board_in: list[list[int]]) -> int:

	position, mask = getBitBoard(starting_player, board_in)
	maxMove = -1
	maxVal = -100
	search_list = []
	for i in [3,2,4,1,5,0,6]:
		#Checkt, ob noch Platz in der Column ist
		if((mask + (1 << i*7) >> i*7) & 64 != 0):
			continue
		#Setzt Stein
		new_position, new_mask = make_move(position, mask, i)
		#Checkt ob die eigene Position gewonnen ist
		own_position = new_position ^new_mask
		if(isGameOver(own_position)):
			return  i
		if(canEndGame(new_position, new_mask)):
			continue
		search_list.append(i)
	if(len(search_list) == 1):
		return search_list[0]
	if(len(search_list) == 0):
			for i in [3,2,4,1,5,0,6]:
				#Checkt, ob noch Platz in der Column ist
				if((mask + (1 << i*7) >> i*7) & 64 == 0):
					return i


	for i in search_list:
		#Checkt, ob noch Platz in der Column ist
		if((mask + (1 << i*7) >> i*7) & 64 != 0):
			print("continue")
			continue
		new_position, new_mask = make_move(position, mask, i)
		own_position = new_position ^new_mask
		value = -evaluationHelper(starting_player, (1-starting_player), new_position, new_mask, maxVal, 100)
		if(value > maxVal):
			maxVal = value
			print("Maxval: " + str(maxVal))
			maxMove = i
		print("Maxmove: " + str(maxMove))
	return maxMove
@lru_cache
def evaluationHelper(initial_player:int, player: int, position: int, mask: int, alpha: int, beta: int) -> int:
	maxVal = -100 if initial_player == player else 100
	placedStone = False
	global nodes_searched
	nodes_searched += 1
	if(nodes_searched % 100000 == 0):
		print(nodes_searched)
	search_list = []
	searchable = False
	for i in [3,2,4,1,5,0,6]:
		#Checkt, ob noch Platz in der Column ist
		if((mask + (1 << i*7) >> i*7) & 64 != 0):
			continue
		searchable = True
		#Setzt Stein
		new_position, new_mask = make_move(position, mask, i)
		#Checkt ob die eigene Position gewonnen ist
		own_position = new_position ^new_mask
		if(isGameOver(own_position)):
			return  (22 -  bin(own_position).count("1"))
		if(canEndGame(new_position, new_mask)):
			continue
		search_list.append(i)
	if(len(search_list) == 0):
		return -(22 -  bin(own_position).count("1")-1) if searchable else 0
	for i in search_list:
		#Checkt, ob noch Platz in der Column ist
		if((mask + (1 << i*7) >> i*7) & 64 != 0):
			continue
		#Setzt Stein
		placedStone = True
		new_position, new_mask = make_move(position, mask, i)
		#Checkt ob die eigene Position gewonnen ist
		value = -evaluationHelper(initial_player, (1-player), new_position, new_mask, alpha, beta)
		if(initial_player == player):
			if value > 0:
				return value
			maxVal = max(maxVal, value)
			alpha = max(alpha, value)
			if(beta <= alpha):
				return maxVal
		else:
			maxVal = min(maxVal, value)
			beta = min(beta, maxVal)
			if(beta <= alpha):
				return maxVal
		
	return  maxVal

"""
Returns whether a position can be won in 1 Move
"""
def canEndGame(position: int, mask: int) -> bool:
	m = position & (position >> 7)
	new_position = (m << 14) & (m << 21)
	#Horizontal ->
	if new_position and new_position & (~mask) :
		return True
	#Horizontal middle ->
	new_position = (m<<14) & (position >> 7)
	if new_position and new_position & (~mask) :
		return True
	#Horizontal middle <-
	new_position = (m>>7) & (position << 7)
	if new_position and new_position & (~mask) :
		return True
	#Horizontal <-
	new_position = (m >> 7)  & (m >> 14)
	if new_position and new_position & (~mask) :
		return True

	# Diagonal \ ->
	m = position & (position >> 6)
	new_position = (m << 12) & (m >> 18)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Diagonal \ middle ->
	new_position = (m << 12) & (position >> 6)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Diagonal \ middle <-
	new_position = (m >> 6) & (position << 6)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Diagonal \ <-
	new_position = (m >> 12) & (m >> 6)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True

	# Diagonal / ->
	m = position & (position >> 8)
	new_position = (m << 16) & (m << 24)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Diagonal / middle ->
	new_position = (m << 16) & (position >> 8)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
		# Diagonal / middle <-
	new_position = (m >> 8) & (position << 8)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Diagonal / <-
	new_position = (m << 8) & (m << 16)
	if new_position and new_position & (~mask) and not (new_position >> 1 & (~mask) ) :
		return True
	# Vertical up
	m = position & (position >> 1)
	new_position = m & (m >> 1)
	
	if new_position and new_position<<3 & (~mask):
		return True
	# Nothing found
	return False

def isGameOver(position: int) -> bool:
	# Horizontal check
	m = position & (position >> 7)
	if m & (m >> 14):
		return True
	# Diagonal \
	m = position & (position >> 6)
	if m & (m >> 12):
		return True
	# Diagonal /
	m = position & (position >> 8)
	if m & (m >> 16):
		return True
	# Vertical
	m = position & (position >> 1)
	if m & (m >> 2):
		return True
	# Nothing found
	return False


"""
Calculates score
"""
def evaluateBoard(self,player: int, board: int, mask: int) -> int:
	if(isGameOver(board)):
		return 22 - bin(board).count("1")
	elif(isGameOver(board ^mask)):
		return 22 - bin(board ^ mask).count("1")
	elif bin( mask).count("1") == 42:
		return 0
	else:
		return -1


board_in = [
	[0, 0, 0, 0, 0, 0, 0,],
	[0, 0, 0, 2, 0, 0, 0,],
	[0, 0, 1, 1, 0, 0, 0,],
	[0, 0, 2, 1, 2, 0, 0,],
	[0, 0, 2, 2, 1, 0, 0,],
	[0, 0, 2, 1, 1, 2, 0,],
]
for i in range(len(board_in)):
	for j in range(len(board_in[i])):
		board_in[i][j] -= 1
	print(board_in[i])
print("\n")
position, mask = getBitBoard(0, board_in)
cur_player = 0
draw = False
while(not isGameOver(position) and not isGameOver(position^mask) and not draw):
	printBoard(board_in)	
	start_time = time.time()
	max_move = evaluationRoot(cur_player, board_in)
	if(max_move == -1):
		raise TypeError("Du Hund")
	position, mask = make_move(position, mask, max_move)
	print("Time to calculate:" + str(time.time() -start_time))
	print("\n\n")
	cur_player = 1 - cur_player
	board_in = getBoardFromBitstring(cur_player, position, mask)
	

	draw = True
	for i in range(width):
		if(board_in[0][i] != EMPTY):
			draw = False
printBoard(board_in)	