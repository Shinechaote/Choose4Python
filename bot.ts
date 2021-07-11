const EMPTY: number = -1;
const PLAYER_1: number = 0;
const PLAYER_2: number = 1;
const width: number = 7;
const height: number = 6;


/**
 * Makes move on bitboard
 * @param position Bitstring representation of the current players pieces
 * @param mask Bitstring representation of all pieces
 * @param col  Column where the piece should be dropped
 * @returns [Enemies pieces as bitstring, all pieces as bitstring]
 */
function makeMove(position: number, mask: number, col: number) : [number, number]
{
	var new_position:number = position ^ mask;
	var new_mask = mask | (mask + (1 << col*width));
	return [new_position, new_mask];
}

/**
 * Prints board
 * @param board 
 */
function printBoard(board: number[][]): void
{
	for(var i:number = 0; i<height;i++)
	{
		console.log(board[i].map(x => x+1));
	}
}

/**
 * Creates the bitstring representation of the players pieces and of all pieces. Enemies pieces can be calculated by XOR
 * Indexes of positions for bitstring (extra row is needed for checking game over states):
 * 
 * | 06 | 13 | 20 | 27 | 34 | 41 | 48 |
 * -----------------------------------
 * | 05 | 12 | 19 | 26 | 33 | 40 | 47 | 
 * | 04 | 11 | 18 | 25 | 32 | 39 | 46 |
 * | 03 | 10 | 17 | 24 | 31 | 38 | 45 |
 * | 02 | 09 | 16 | 23 | 30 | 37 | 44 | 
 * | 01 | 08 | 15 | 22 | 29 | 36 | 43 |
 * | 00 | 07 | 14 | 21 | 28 | 35 | 42 |
 * ------------------------------------
 * 
 * @param player Player's number in the board
 * @param board  The 2d-Array representing the board
 * @returns  [positions of player's pieces, positions of every piece]
 */
function getBitBoard(player: number, board: number[][]): [number, number]
{
	var position: number = 0;
	var mask : number = 0;
	for(var i: number = 0;i<height;i++)
	{
		for(var j: number= 0; j<width;j++)
		{
			position += board[i][j] == player ? 1 << (j*width + height-i-1) : 0;
			position += board[i][j] != EMPTY ? 1 << (j*width + height-i-1) : 0;
		}
	}

	return [position, mask];
}

/**
 * Creates a 2d-Array representing a board using given bitstring representations
 * @param currentPlayer Player to whom the position bitstring belongs
 * @param position Bitstring of player's pieces
 * @param mask Bitstring of all pieces
 * @returns 2d-Array representing the given state of the board
 */
function getBoardFromBitstring(currentPlayer: number, position: number, mask: number): number[][]
{
	var board: number[][] = new Array(height);
	for(var i: number =0;i<height;i++)
	{
		board[i] = new Array(width);
		for(var j: number = 0; j<width;j++)
		{
			if((mask >> (j*7 + i) & 1) != 1)
			{
				board[i][j] = EMPTY
			}
			else
			{
				board[i][j] = (position >> (j*7 + i) & 1) ? currentPlayer : (1-currentPlayer);
			}
		}
	}
	return board;
}

/**
 * Counts the number of set bits in the given number
 */
 function countOnes(n: number)
 {
	 return n.toString(2).replace(/0/g,"").length;
 }

/**
 * Root of an evaluation Tree. A board is only evaluated once it's completed.
 * The winner gets 22 - (#played pieces from him) points.
 * Using alpha-beta pruning the search tree is cut down. Also the tree only searches for
 * a winning strategy not an optimal strategy.
 * @param starting_player Player for which the optimal move should be found
 * @param board The current state of the board represented as a 2d-Array
 * @returns The column of the optimal move
 */
function evaluationRoot(starting_player: number, board: number[][]): number
{
	var position: number;
	var mask: number;
	[position, mask] = getBitBoard(starting_player, board);
	if(isGameOver(position))
	{
		throw new TypeError("Board is already finished");
	}
	var maxMove: number =-1;
	var maxVal: number = -100;
	var searchList = [];
	var searchPreferences: number[] = [3,2,4,1,5,0,6];
	var draw: boolean = true;
	for(var j: number = 0;j<width;j++)
	{
		var i: number = searchPreferences[j];
		if(((mask + (1 << i*7) >> i*7) & 64) != 0)
		{
			continue;
		}
		//Sets stone
		draw = false;
		var new_position: number;
		var new_mask: number;
		[new_position, new_mask] = makeMove(position, mask, i)
		//Checks whether own position is won
		var own_position: number = new_position ^new_mask
		if(isGameOver(own_position))
		{
		return  i;
		}
		//Checks whether enemy can win within 1 move
		if(canEndGame(new_position, new_mask))
		{	continue;
	}
		searchList.push(i);	
	}
	if(draw)
	{
		throw new TypeError("Board is already finished");
	}
	//If there's only one not-losing move, return it
	if(searchList.length == 1)
	{
		return searchList[0];
	}
	//If there's no not-losing move, just return a random valid move
	if(searchList.length == 0)
	{
		for(var j = 0; j< width;j++)
		{
			var i = searchPreferences[j];
			if(((mask + (1 << i*7) >> i*7) & 64) == 0)
			{
				return i;
			}
		}
	}
	for(var j: number = 0;j<searchList.length;j++)
	{
		var i: number = searchList[j]; 
		//Checks, whether a piece can be put in column i
		if(((mask + (1 << i*7) >> i*7) & 64) != 0){
			console.log("continue")
			continue
		}
		var new_position: number;
		var new_mask: number;
		[new_position, new_mask] = makeMove(position, mask, i)
		own_position = new_position ^new_mask
		//Get's value of next node but inverting to get value for the maximizing player
		var value: number = -evaluationHelper(starting_player, (1-starting_player), new_position, new_mask, maxVal, 100)
		if(value > maxVal){
			maxVal = value
			console.log("Maxval: " + String(maxVal))
			maxMove = i
		console.log("Maxmove: " + String(maxMove))
		}
	return maxMove
	}


	return 0;
}

/**
 * Represents a node of the search tree. For more detail check evaluationRoot()
 * @param initial_player The player for which the value should be maximized
 * @param player The current playing player
 * @param position Bitstring of player's pieces in this node
 * @param mask Bitstring of all pieces of this node
 * @param alpha Best guaranteed value of maximizing player
 * @param beta Best guaranteed value of minimizing player
 * @returns The best value for the current player (NOT the initial player)
 */
function evaluationHelper(initial_player:number, player: number, position: number, mask: number, alpha: number, beta: number): number
{
	var maxVal: number = initial_player == player ? -100 : 100;
	var	search_list: number[] = [];
	var searchPreferences = [3,2,4,1,5,0,6];
	var searchable: boolean = false;
	for (var j: number = 0;j<width;j++) {
		var i: number = searchPreferences[j];
		//Checks, whether a piece can be put in column i
		if(((mask + (1 << i*7) >> i*7) & 64) != 0){
			continue
		}
		searchable = true
		//Sets piece
		var new_position: number;
		var new_mask: number;
		[new_position, new_mask] = makeMove(position, mask, i)
		//Checks, whether own position is won
		var own_position: number = new_position ^new_mask
		if(isGameOver(own_position)){
			return  (22 -  countOnes(own_position))
		}
		if(canEndGame(new_position, new_mask))
		{
			continue
		}
		search_list.push(i)
	}
	if(search_list.length == 0){
		return searchable ? -(22 -  countOnes(own_position)-1) : 0;
	}
	for (var j: number = 0;j<width;j++) {
		var i: number = searchPreferences[j];
		//Checks, whether a piece can be put in column i
		if(((mask + (1 << i*7) >> i*7) & 64) != 0)
		{
			continue
		}
		//Sets piece
		var new_position: number;
		var new_mask: number;
		[new_position, new_mask] = makeMove(position, mask, i)
		var value: number = -evaluationHelper(initial_player, (1-player), new_position, new_mask, alpha, beta)
		//Updates alpha and beta values
		if(initial_player == player){
			//If we find a guaranteed winning value, we take it
			if (value > 0){
				return value
			}
			//If the best move reduces the guaranteed value of the minimizer we skip the node
			//because the minimizer will never take this choice
			maxVal = value > maxVal ? value : maxVal;
			alpha = maxVal > alpha ? value : alpha;
			if(beta <= alpha){
				return maxVal
			}
		}
		else{
			maxVal = value < maxVal ? value : maxVal;
			beta = maxVal < beta ? value : beta;
			if(beta <= alpha){
				return maxVal
			}
		}
	}
	return  maxVal
}

function isGameOver(position: number): boolean
{
	// Horizontal check
	var m: number = position & (position >> 7)
	if (m & (m >> 14))
		return true
	// Diagonal \
	m = position & (position >> 6)
	if (m & (m >> 12))
		return true
	// Diagonal /
	m = position & (position >> 8)
	if( m & (m >> 16))
		return true
	// Vertical
	m = position & (position >> 1)
	if( m & (m >> 2))
		return true
	// Nothing found
	return false
}

function canEndGame(position: number, mask: number): boolean
{
	var m = position & (position >> 7)
	var new_position = (m << 14) & (m << 21)
	//Horizontal ->
	if (new_position && new_position & (~mask))
		return true
	//Horizontal middle ->
	new_position = (m<<14) & (position >> 7)
	if (new_position && new_position & (~mask))
		return true
	//Horizontal middle <-
	new_position = (m>>7) & (position << 7)
	if (new_position && new_position & (~mask) )
		return true
	//Horizontal <-
	new_position = (m >> 7)  & (m >> 14)
	if (new_position && new_position & (~mask) )
		return true

	// Diagonal \ ->
	m = position & (position >> 6)
	new_position = (m << 12) & (m >> 18)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ))
		return true
	// Diagonal \ middle ->
	new_position = (m << 12) & (position >> 6)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
	// Diagonal \ middle <-
	new_position = (m >> 6) & (position << 6)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
	// Diagonal \ <-
	new_position = (m >> 12) & (m >> 6)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true

	// Diagonal / ->
	m = position & (position >> 8)
	new_position = (m << 16) & (m << 24)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
	// Diagonal / middle ->
	new_position = (m << 16) & (position >> 8)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
		// Diagonal / middle <-
	new_position = (m >> 8) & (position << 8)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
	// Diagonal / <-
	new_position = (m << 8) & (m << 16)
	if (new_position && new_position & (~mask) && ! (new_position >> 1 & (~mask) ) )
		return true
	// Vertical up
	m = position & (position >> 1)
	new_position = m & (m >> 1)
	
	if (new_position && new_position<<3 & (~mask))
		return true
	// !hing found
	return false
}