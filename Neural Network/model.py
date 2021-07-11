import random
from pygad.torchga.torchga import model_weights_as_dict
import torch
from torch.functional import Tensor
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):

	def __init__(self) -> None:
		super(Net, self).__init__()
		self.fc1 = nn.Linear(7*6, 42)
		self.fc2 = nn.Linear(42,35)
		self.fc3 = nn.Linear(35,24)
		self.fc4 = nn.Linear(24,14)
		self.fc5 = nn.Linear(14,7)
		torch.nn.init.kaiming_uniform_(self.fc1.weight)
		self.fc1.bias.data.fill_(0.02)
		torch.nn.init.kaiming_uniform_(self.fc2.weight)
		self.fc2.bias.data.fill_(0.02)
		torch.nn.init.kaiming_uniform_(self.fc3.weight)
		self.fc3.bias.data.fill_(0.02)
		torch.nn.init.kaiming_uniform_(self.fc4.weight)
		self.fc4.bias.data.fill_(0.02)
		torch.nn.init.kaiming_uniform_(self.fc5.weight)
		self.fc5.bias.data.fill_(0.02)
	
	def forward(self, board) -> Tensor:
		flatBoard = [20*item for row in board for item in row]
		x = torch.Tensor(flatBoard)
		x = F.relu(self.fc1(x))
		x = F.relu(self.fc2(x))
		x = F.relu(self.fc3(x))
		x = F.relu(self.fc4(x))
		x = self.fc5(x)
		return x


class Model:
	def __init__(self,weights, width :int = 7, height:int=6, index:int=0) -> None:
		self.width = width
		self.height = height
		self.index = index
		self.net = Net()
		if(weights != None):
			self.net.load_state_dict(weights)
	
	def getMove(self, board: list[list[int]], possibleMoves: list[int]) -> int:
		if(sum(possibleMoves) == 0):
			raise ValueError("There are no possible options")
		moves = self.net(board)
		moves = [moves[i] * possibleMoves[i] for i in range(len(moves))]
		move = moves.index(max(moves))
		if(possibleMoves[move] == 0):
			return possibleMoves.index(max(possibleMoves))
		return move