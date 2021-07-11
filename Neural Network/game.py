from fourInARow import Game
from model import Model, Net
import numpy as np
import random
import pygad.torchga as torchga
import torch
import math

WIDTH = 7
HEIGHT = 6
SIZE_PARENTS_POOL = 8
SIZE_TOURNAMENT = 256
CROSSOVER_PROBABILITY = 0.78
MUTATION_PROBABILITY = 0.03
MUTATION_MAX_VAL = 1
MUTATION_MIN_VAL = -1
EPOCHS = 3000


def evolution(weights = None):
	models = [Model(weights, index=i) for i in range(SIZE_TOURNAMENT)]
	bestScore = -1
	bestModels = []
	for i in range(EPOCHS):
		models, ratio = genetic_step(models)
		if(ratio > bestScore):
			bestScore = ratio
			bestModels = models
		if(i % 10 == 0):
			print(str(i) + ": " + str(ratio))
		if(i % 50 == 0):
			gameModels, ratio = createTournament(models, skipRounds=1)
			createGame(gameModels[0], gameModels[1], printBoard=True)
		if(i % 1000 == 0):
			torch.save(createTournament(models, skipRounds=0)[0][0].net.state_dict(), "./winner2.pt")
	tup = (createTournament(models, skipRounds=0)[0][0],createTournament(bestModels, skipRounds=0)[0][0])
	print(tup)
	return tup


def genetic_step(models: list[Model]):
	parentModels, ratio = createTournament(models, skipRounds=math.floor(math.log2(SIZE_PARENTS_POOL)))
	newGeneration = crossover(parentModels)
	newGeneration = mutate(newGeneration)

	return ([Model(torchga.model_weights_as_dict(Net(),newGeneration[i])) for i in range(len(newGeneration))], ratio)

def mutate(offspring):
	for offspring_idx in range(offspring.shape[0]):
		probs = np.random.random(size=offspring.shape[1])
		for gene_idx in range(offspring.shape[1]):
			if probs[gene_idx] <= MUTATION_PROBABILITY:
				# Generating a random value.
				random_value = np.random.uniform(low=MUTATION_MIN_VAL, 
													high=MUTATION_MAX_VAL, 
													size=1)
				# If the mutation_by_replacement attribute is True, then the random value replaces the current gene value.
				random_value = offspring[offspring_idx, gene_idx] + random_value
				random_value = np.round(random_value)
				offspring[offspring_idx, gene_idx] = random_value
	return offspring

def crossover(parents: list[Model]) -> np.array:
	parents_genes = np.array([torchga.model_weights_as_vector(model=parent.net) for parent in parents])
	
	offspring = np.empty((SIZE_TOURNAMENT, parents_genes[0].shape[0]), dtype=float)
	for k in range(SIZE_TOURNAMENT):
		probs = np.random.random(size=parents_genes.shape[0])
		indices = np.where(probs <= CROSSOVER_PROBABILITY)[0]

		# If no parent satisfied the probability, no crossover is applied and a parent is selected.
		if len(indices) == 0:
			offspring[k, :] = parents_genes[k % parents_genes.shape[0], :]
			continue
		elif len(indices) == 1:
			parent1_idx = indices[0]
			parent2_idx = parent1_idx
		else:
			indices = random.sample(list(indices), 2)
			parent1_idx = indices[0]
			parent2_idx = indices[1]
		genes_source = np.random.randint(low=0, high=2, size=parents_genes[0].shape[0])
		for gene_idx in range(parents_genes[0].shape[0]):
			if (genes_source[gene_idx] == 0):
				# The gene will be copied from the first parent if the current gene index is 0.
				offspring[k, gene_idx] = parents_genes[parent1_idx, gene_idx]
			elif (genes_source[gene_idx] == 1):
				# The gene will be copied from the second parent if the current gene index is 1.
				offspring[k, gene_idx] = parents_genes[parent2_idx, gene_idx]
	return offspring


def createTournament(models: list[Model], skipRounds = 0) -> Model:
	rounds = math.floor(math.log2(len(models)))
	players = 2** rounds
	models = models[0:players]
	newModels = []
	totalLength = 0
	gamesPlayed = 0
	for round in range(rounds-skipRounds):
		for gameIndex in range(len(models)//2):
			winner, length = createGame(model1=models[gameIndex*2],model2=models[2*gameIndex +1])
			gamesPlayed += 1
			totalLength += length
			newModels.append(models[2*gameIndex] if winner == 0 else models[2*gameIndex+1])
		models = newModels
		newModels = []
	return (models,totalLength/gamesPlayed)

def createGame(model1: Model, model2: Model, printBoard = False) -> int:
	if(model1.width != WIDTH or model2.width != WIDTH):
		raise ValueError("createGame: Widths do not match up")
	game = Game(WIDTH,HEIGHT)
	curPlayer = 0
	length = 0
	while(not game.isGameOver()):
		possibleMoves = game.getMoves()
		move = -1
		if(curPlayer == 0):
			move = model1.getMove(game.board, possibleMoves)
		else:
			move = model2.getMove(game.board, possibleMoves)
		game.putOnBoard(move)
		length += 1
		curPlayer = 1-curPlayer
	if(printBoard):
		game.printBoard()
		print()
	return (game.winner, length)



winnerModel, bestModel = evolution(weights = torch.load("./winner1.pt"))
torch.save(winnerModel.net.state_dict(), "./winner2.pt")
game = Game()
createGame(winnerModel, bestModel, printBoard=True)
while not game.isGameOver():
	game.printBoard()
	game.putOnBoard(winnerModel.getMove(game.board, game.getMoves()))
	game.printBoard()
	game.putOnBoard(int(input("Column: "))-1)
game.printBoard()