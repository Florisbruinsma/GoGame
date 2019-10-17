import numpy as np
import random
class ObservationSpace:
    def __init__(self, boardSize=5):
        self.shape = (boardSize*boardSize,)
class ActionSpace:
    def __init__(self, boardSize=5):
        self.n = boardSize*boardSize
class GoGame:
    def __init__(self, boardSize=5):
        self.boardSize = boardSize
        self.currentBoard = np.zeros((boardSize,boardSize), dtype = int)#current state of the board as 2d array
        self.boardHistory = np.expand_dims(np.zeros((boardSize,boardSize), dtype = int),axis=0)#history of all the turns as 3d array, first axis is turn amount
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)#list of part of the board that is checked already
        self.players = [0,1,2]# neutral, p1, p2
        self.captures = [0,0,0]#amount of stones that where captures from the corresponding player
        self.stones = [0,0,0]#amount of stones on the board fo player
        self.scores = [0,0,0]
        self.groups = [],[],[]
        self.currentTurn = 0
        self.action_space = ActionSpace(boardSize)
        self.observation_space = ObservationSpace(boardSize)

    def restartGame(self, boardSize=5):
        """
            resets all values, thereby restarting the game
        Parameters
        ----
            boardSize : int, the size of the board
        Returns
        ----
            nothing
        """
        self.boardSize = boardSize
        self.currentBoard = np.zeros((boardSize,boardSize), dtype = int)#current state of the board as 2d array
        self.boardHistory = np.expand_dims(np.zeros((boardSize,boardSize), dtype = int),axis=0)#history of all the turns as 3d array, first axis is turn amount
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)#list of part of the board that is checked already
        self.players = [0,1,2]# neutral, p1, p2
        self.captures = [0,0,0]#amount of stones that where captures from the corresponding player
        self.stones = [0,0,0]#amount of stones on the board fo player
        self.scores = [0,0,0]
        self.groups = [],[],[]
        self.passMove = [0,0]
        self.currentTurn = 0

    def printBoard(self, board="currentBoard"):
        """
            print the given game board with player 1 as x and player 2 as o
        Parameters
        ----
            board : 2d array with shape boardSize,boardSize
        Returns
        ----
            nothing
        """
        if(board == "currentBoard"):
            board = self.currentBoard
        print('\n ',end='')
        for col in range(self.boardSize):
            print(col,end='')
        print('')
        for row in range(self.boardSize):
            print(row,end='')
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
            revert the current board back to a given turn
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
            currentBoard: 2d array of how the current board is after the move
            score: array with the score of all players
            done: bool true if game is over
        """
        if(passMove == True):
            self.passMove[player] = True
            if(self.passMove[0] == True and self.passMove[1] == True):
                return self.currentBoard, self.scores, True
            else:
                return self.currentBoard, self.scores, False
        if(not self.checkValidMove(coord,player)):
            # print("invalid_move")
            return False
        self.currentBoard[coord] = player
        self.stones[player] += 1
        self.resolveTurn(player)
        self.boardHistory = np.vstack((self.boardHistory,np.expand_dims(self.currentBoard,axis=0)))
        self.currentTurn += 1
        self.countScore()
        return self.currentBoard, self.scores, False

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

    def checkValidMove(self,coord, player):
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

    def extendChains(self,coord,val,list1=[]):
        """
            use recursion to find a complete chain that is connected from the coordinate
        Parameters
        ----
            coord : tuple, coord is used as (row,col)
            val: int, state of a stone, can be 0, 1 or 2
        Returns
        ----
            list of the full chain
        """
        list1.append(coord)
        self.boardCheck[coord] = 1#do this board check to make sure the first coord isn't added dubbel
        new_list = []
        connections = [(coord[0]+1,coord[1]),(coord[0],coord[1]+1),(coord[0]-1,coord[1]),(coord[0],coord[1]-1)]
        for coord in connections:
            if(max(coord)<self.boardSize and min(coord) >= 0 and self.boardCheck[coord] == 0 and self.currentBoard[coord] == val):
                new_list.append(coord)
                self.boardCheck[coord] = 1
        for coord in new_list:
            list1.extend(self.extendChains(coord,val,[]))
        return list1

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
            removes all stones in given chain from the board and 
        Parameters
        ----
            chain : list of tuple coordinates (row,col)
        Returns
        ----
            nothing
        """
        for coord in chain:
            self.currentBoard[coord] = 0

    def countScore(self):
        """
            counts the total score per player for existing groups and captured stones
        Parameters
        ----
            None
        Returns
        ----
            the scores of all players
        """
        for player in self.players:
            total_amount = 0
            for chain in self.groups[player]:
                total_amount += len(chain)
            total_amount -= self.captures[player]
            self.scores[player] = total_amount

        return self.scores

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
                    chains[self.currentBoard[row][col]].append(self.extendChains((row,col),self.currentBoard[row][col],[]))
        #check for captures
        for chain in chains[second_player]:
            if(len(self.getLiberties(chain)) == 0):
                self.captures[second_player] += len(chain)
                self.stones[second_player] -= len(chain)
                self.removeStones(chain)
                capture = True
        for chain in chains[first_player]:
            if(len(self.getLiberties(chain)) == 0):
                self.captures[first_player] += len(chain)
                self.stones[first_player] -= len(chain)
                self.removeStones(chain)
                capture = True
        if capture:
            self.resolveTurn(player)
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

    def getCurrentBoard(self):
        return self.currentBoard

    def getAllValidMoves(self, player):
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
        moves = self.getAllValidMoves(player)
        return random.choice(moves)

    def coordToFlatMove(self, coord):
        flat_move = coord[0]*self.boardSize+coord[1]
        return flat_move

    def flatMoveToCoord(self, flat_move):
        coord=[0,0]
        coord[0] = int(flat_move / self.boardSize)
        coord[1] = flat_move % self.boardSize
        if(coord[0]>=self.boardSize or  coord[1]>=self.boardSize):
            coord = [0,0]
        return tuple(coord)

    def boardToTri(self, board="currentBoard"):
        if(str(board) == "currentBoard"):
            board = self.currentBoard
        return int(''.join(map(str, board.flatten())))

    def decToTri(self, dec_num):
        if dec_num == 0:
            return 0
        nums = []
        while dec_num:
            dec_num, remain = divmod(dec_num, 3)
            nums.append(str(remain))
        return int(''.join(reversed(nums)))

    def TriToDec(self, tri_num):
        dec_num = 0                     # output sum
        inc = 1                     # incrementing number (what you multiply each digit by)
        while tri_num:
            digit = inc * (tri_num % 10)  # last digit of a times the incrementer
            dec_num += digit            # digit added to sum
            tri_num //= 10                # cuts off the last digit of a (// is integer division in python 3.x)
            inc *= 3             # base (2 for binary, 3 for ternary, etc)
        return dec_num

##-----functionalities to make this class feel just like open ai gym-----
    def step(self, action):
        reward = 0
        move = self.flatMoveToCoord(action)
        if(not self.takeTurn(move, 1)):
            reward = -100
        self.takeTurn(self.getRandomMove(2), 2)#let ai take random move
        next_state = self.currentBoard.flatten()
        if(reward == 0):
            reward = self.scores[1] - self.scores[2]
        if(self.currentTurn >= 20):
            done = True
        else:
            done = False
        info = "Go game"
        return next_state, reward, done, info

    def reset(self, boardSize=5):
        scores = self.scores
        self.restartGame(boardSize)
        obs = self.currentBoard.flatten()
        return obs

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