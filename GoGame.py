import numpy as np
import random
class ObservationSpace:
    def __init__(self, boardSize=5):
        self.shape = (boardSize*boardSize,)
class ActionSpace:
    def __init__(self, boardSize=5):
        self.n = boardSize*boardSize
class GoGame:
    def __init__(self, boardSize=5, maxTurns=30):
        """
            initiates all variables needed for 
        Parameters
        ----
            boardSize : int size of the dimensions of the board
            Maxturns : when using the step functtion for rl this is the amount of turn afterw hich a game will be ended
        Returns
        ----
            nothing
        """
        self.boardSize = boardSize#dimensions of the board
        self.maxTurns = maxTurns#maximum amount of turns that can be taken with the step function
        self.currentBoard = np.zeros((boardSize,boardSize), dtype = int)#current state of the board as 2d list
        self.boardHistory = np.expand_dims(np.zeros((boardSize,boardSize), dtype = int),axis=0)#history of all the turns as 3d list, first axis is turn amount
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)#used to make sure places on the board dont get checked twice
        self.players = [0,1,2]# neutral, p1, p2
        self.captures = [0,0,0]#amount of stones that where captures from the corresponding player
        self.scores = [0,0,0]#scores of the players
        self.groups = [],[],[]
        self.passMove = [0,0]
        self.currentTurn = 0
        self.action_space = ActionSpace(boardSize)
        self.observation_space = ObservationSpace(boardSize)

    def restartGame(self):
        """
            resets all changed values, thereby restarting the game
        Returns
        ----
            nothing
        """
        # for comments on the variables look at the __init__
        self.currentBoard = np.zeros((self.boardSize,self.boardSize), dtype = int)
        self.boardHistory = np.expand_dims(np.zeros((self.boardSize,self.boardSize), dtype = int),axis=0)
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)
        self.captures = [0,0,0]
        self.scores = [0,0,0]
        self.groups = [],[],[]
        self.passMove = [0,0]
        self.currentTurn = 0

    def printBoard(self, specific_board=False):
        """
            print the given game board with player 1 as x and player 2 as o
        Parameters
        ----
            specific_board : 2d list with shape boardSize,boardSize
        Returns
        ----
            nothing
        """
        if(not specific_board):
            board = self.currentBoard
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                if(board[row][col] == 0):
                    print('-',end='')
                elif(board[row][col] == 1):
                    print('x',end='')
                elif(board[row][col] == 2):
                    print('o',end='')
            print('')

    def revertBoard(self, turn):
        """
            revert the current board back to the given turn
        Parameters
        ----
            turn : int, value of the turn you want to revert to
        Returns
        ----
            nothing
        """
        if(self.currentTurn <= turn):
            return
        else:
            self.currentBoard = self.boardHistory[turn]
            self.currentTurn = turn
            self.boardHistory = self.boardHistory[:turn+1]

    def takeTurn(self, coord, player, passMove = False):
        """
            handles everything that happens during a turn
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
            player: int, number of the player, can be 1 or 2
            passMove: bool set this as true if you want to pass
        Returns
        ----
            done: bool true if game is over
        """
        if(passMove == True):
            self.passMove[player] = True
            if(self.passMove[0] == True and self.passMove[1] == True):
                return True
            else:
                return False
        if(not self.checkValidMove(coord,player)):
            return False
        self.currentBoard[coord] = player
        self.resolveTurn(player)
        self.boardHistory = np.vstack((self.boardHistory,np.expand_dims(self.currentBoard,axis=0)))
        self.currentTurn += 1
        self.updateScore()
        return True

    def resolveTurn(self,player):
        """
            resolves everything that happens after a stone is placed. Like stone captures, and tries to find the current groups, for the score
        Parameters
        ----
            player : int can be 1 or 2 is used to determine which pieces to capture first
        Returns
        ----
            nothing
        """
        # assign every space on the board to a chain
        capture = False
        chains = [],[],[]
        self.groups = [],[],[]
        first_player = 1 if (player==1) else 2#which player played this turn, so captures can be checked first for the oponent
        second_player = 2 if (player==1) else 1
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)
        #create and extend chains
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                if(self.boardCheck[row][col] == 0):
                    chains[self.currentBoard[row][col]].append(self.extendChains((row,col),self.currentBoard[row][col]))
        #check for captures
        for chain in chains[second_player]:
            if(len(self.getLiberties(chain)) == 0):
                self.captures[second_player] += len(chain)
                self.removeStones(chain)
                capture = True
        for chain in chains[first_player]:
            if(len(self.getLiberties(chain)) == 0):
                self.captures[first_player] += len(chain)
                self.removeStones(chain)
                capture = True
        if capture:
            self.resolveTurn(player)#something has changed on the board so we will check for captures again
            return
        #add some of the neutral chains to player groups
        self.groups[1].extend(chains[1])
        self.groups[2].extend(chains[2])
        for chain in chains[0]:
            connection = []
            for coord in chain:
                connection.extend(self.checkNeighbours(coord))
            if (not(2 in connection) and 1 in connection):
                self.groups[1].append(chain)
            elif (not(1 in connection) and 2 in connection):
                self.groups[2].append(chain)
            else:
                self.groups[0].append(chain)

    def checkNeighbours(self,coord):
        """
            check the neighbours of a coordinate
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
        Returns
        ----
            return a list with [top,right,down,left] neighbour with value 0,1,2 or 3 with 3 being oob
        """
        connections = [(coord[0]+1,coord[1]),(coord[0],coord[1]+1),(coord[0]-1,coord[1]),(coord[0],coord[1]-1)]
        neighbours = []
        for coord in connections:
            if(max(coord)>=self.boardSize or min(coord) < 0):
                neighbours.append(3)
            else:
                neighbours.append(self.currentBoard[coord])
        return neighbours

    def checkValidMove(self, coord, player):
        """
            check if a move is valid
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
            player: int, number of the player, can be 1 or 2
        Returns
        ----
            bool
        """
        # check if coord is within bounds
        if(max(coord) >= self.boardSize or min(coord) < 0):
            return False
        # check if position is already filled
        if(self.currentBoard[coord] != 0):
            return False
        neighbours = self.checkNeighbours(coord)
        # check for suicide move
        if(not((player == 1 and (1 in neighbours or 0 in neighbours)) or (player == 2 and (2 in neighbours or 0 in neighbours)))):
            return False
        return True

    def extendChains(self,coord,val,chain_list=None):
        """
            use recursion to find every stone in the chain that is connected from the coordinate
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
            val: int, state of a stone, can be 0, 1 or 2
        Returns
        ----
            list of the full chain
        """
        if(chain_list==None):
            chain_list=[]
        chain_list.append(coord)
        self.boardCheck[coord] = 1#do this board check to make sure the first coord isn't added dubbel
        new_list = []
        connections = [(coord[0]+1,coord[1]),(coord[0],coord[1]+1),(coord[0]-1,coord[1]),(coord[0],coord[1]-1)]
        for coord in connections:
            if(max(coord)<self.boardSize and min(coord) >= 0 and self.boardCheck[coord] == 0 and self.currentBoard[coord] == val):
                new_list.append(coord)
                self.boardCheck[coord] = 1
        for coord in new_list:
            chain_list.extend(self.extendChains(coord,val))
        return chain_list

    def getLiberties(self, chain):
        """
            return a list of all liberties of the given chain
        Parameters
        ----
            chain : list of tuple coordinates (row,col)
        Returns
        ----
            list of all the coordinates of liberties
        """
        liberties = []
        for stone in chain:
            connections = [(stone[0]+1,stone[1]),(stone[0],stone[1]+1),(stone[0]-1,stone[1]),(stone[0],stone[1]-1)]
            for coord in connections:
                if(max(coord)<self.boardSize and min(coord) >= 0 and self.currentBoard[coord] == 0):
                    if(not liberties.count(coord)):
                        liberties.append(coord)
        return liberties

    def removeStones(self, chain):
        """
            removes all stones in given chain from the board
        Parameters
        ----
            chain : list of tuple coordinates (row,col)
        Returns
        ----
            nothing
        """
        for coord in chain:
            self.currentBoard[coord] = 0

    def updateScore(self):
        """
            counts the total score per player, you get a point per stone in your group and get 1 point substracted per captured stone
        Parameters
        ----
            None
        Returns
        ----
            the scores of all players
        """
        for player in self.players:
            total_amount = 0
            for group in self.groups[player]:
                total_amount += len(group)
            total_amount -= self.captures[player]
            self.scores[player] = total_amount

        return self.scores

##-----helper functions-----##

    def getAllValidMoves(self, player):
        """
            creates a list of all valid possible moves for the player
        Parameters
        ----
            player: int, number of the player, can be 1 or 2
        Returns
        ----
            list of all the coord's of valid moves for that player
        """
        moves = []
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                coord = (row,col)
                if(self.currentBoard[coord] == 0):
                    neighbours = self.checkNeighbours(coord)
                    if(((player == 1 and (1 in neighbours or 0 in neighbours)) or (player == 2 and (2 in neighbours or 0 in neighbours)))):
                        moves.append(coord)
        return moves

    def getRandomMove(self,player):
        """
            gives you a random alid move for the selected player
        Parameters
        ----
            player: int, number of the player, can be 1 or 2
        Returns
        ----
            coord : tuple, coord is used as (row,col)
        """
        moves = self.getAllValidMoves(player)
        return random.choice(moves)

    def coordToFlatMove(self, coord):
        """
            converts a coord tupple to an int
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
        Returns
        ----
            flat_move : int value of the given coord
        """
        flat_move = coord[0]*self.boardSize+coord[1]
        return flat_move

    def flatMoveToCoord(self, flat_move):
        """
            converts an int to a coord tupple
        Parameters
        ----
            flat_move : int value of the given coord
        Returns
        ----
            coord : tuple, coord is used as (row,col)
        """
        coord=[0,0]
        coord[0] = int(flat_move / self.boardSize)
        coord[1] = flat_move % self.boardSize
        if(coord[0]>=self.boardSize or  coord[1]>=self.boardSize):
            coord = [0,0]
        return tuple(coord)

    def makeRandomMove(self, player):
        """
            makes a random move for the given player
        Parameters
        ----
            player: int, number of the player, can be 1 or 2
        Returns
        ----
            done: bool true if game is over
        """
        return self.takeTurn(self.getRandomMove(player), player)

##-----functionalities to make this class feel just like an open ai gym envirement-----##
    def step(self, action):
        reward = 0
        coord = self.flatMoveToCoord(action)
        if(not self.takeTurn(coord, 1)):
            reward = -100
        self.makeRandomMove(2)#let ai take random move

        state = self.currentBoard.flatten()
        if(reward == 0):
            reward = self.scores[1] - self.scores[2]
        if(self.currentTurn >= self.maxTurns):
            done = True
        else:
            done = False
        info = "Go game"
        return state, reward, done, info

    def reset(self):
        self.restartGame()
        state = self.currentBoard.flatten()
        return state

    def render(self):
        self.printBoard()

# TODO
"""
Create a handicap system, based on board size
Enable or disable if turns should be forced to be alternately between the players
Setting an amount of handicap points for going second
visual interface class
coin toss funcion to decide who goes first
"""