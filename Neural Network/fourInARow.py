class Game:
	EMPTY = -1

	def __init__(self, width = 7, height = 6) -> None:
		self.width = width
		self.height = height
		self.board = [[self.EMPTY for i in range(self.width)] for j in range(self.height)]
		self.curColor = 0
		self.gameOver = False
		self.winner = -1

	def boardFull(self) -> bool:
		for i in range(self.width):
			if(self.board[0][i] == self.EMPTY):
				return False
		return True

	def reset(self):
		self.board = [[self.EMPTY for i in range(self.width)] for j in range(self.height)]
		self.curColor = 0
		self.gameOver = False
		self.winner = -1

	def getMoves(self):
		moves = [0 for i in range(self.width)]
		for i in range(self.width):
			if(self.board[0][i] == self.EMPTY):
				moves[i] = 1
		return moves

	def isGameOver(self) -> bool:
		if(self.gameOver):
			return True
		for i in range(self.height):
			row = self.board[i]
			for j in range(self.width-3):
				if(row[j] == row[j+1] and row[j+1] == row[j+2] and row[j+2] == row[j+3] and row[j] != self.EMPTY):
					self.gameOver = True
					self.winner = row[j]
					return True
		for i in range(self.width):
			column = [self.board[j][i] for j in range(self.height)]
			for j in range(self.height-3):
				if(column[j] == column[j+1] and column[j+1] == column[j+2] and column[j+2] == column[j+3] and column[j] != self.EMPTY):
					self.gameOver = True
					self.winner = column[j]
					return True

		for i in range(self.height-3):
			for j in range(self.width-3):
				diagonal = [self.board[i+k][j+k] for k in range(4)]
				if(diagonal[0] == diagonal[1] and diagonal[1] == diagonal[2] and diagonal[2] == diagonal[3] and diagonal[0] != self.EMPTY):
					self.gameOver = True
					self.winner = diagonal[0]
					return True
				diagonal = [self.board[self.height-(1+i+k)][j+k] for k in range(4)]
				if(diagonal[0] == diagonal[1] and diagonal[1] == diagonal[2] and diagonal[2] == diagonal[3] and diagonal[0] != self.EMPTY):
					self.gameOver = True
					self.winner = diagonal[0]
					return True
		for i in range(self.height):
			for j in range(self.width):
				if(self.board[i][j] == -1):
					return False
		self.gameOver = True
		self.winner = -1
		return True

	def printBoard(self):
		numbers = {0 : "X", 1 : "O", -1: " "}
		for i in range(self.height):
			print([numbers[self.board[i][j]] for j in range(self.width)])
		print("\n")

	def putOnBoard(self,column: int) -> bool:
		if(not self.gameOver):
			if(self.board[0][column] != self.EMPTY or column < 0 or column >= self.width):
				return False
			
			for i in range(self.height):
				if(self.board[i][column] != self.EMPTY):
					self.board[i-1][column] = self.curColor
					self.curColor = 1 -self.curColor
					return True
			self.board[self.height-1][column] = self.curColor
			self.curColor = 1 -self.curColor
			return True
		return False
    
    