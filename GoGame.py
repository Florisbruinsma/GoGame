import numpy as np
class GoGame:
    def __init__(self, boardSize):
        self.boardSize = boardSize
        self.currentBoard = np.zeros((boardSize,boardSize), dtype = int)#current state of the board as 2d array
        self.boardHistory = np.expand_dims(np.zeros((boardSize,boardSize), dtype = int),axis=0)#history of all the turns as 3d array, first axis is turn amount
        self.boardCheck = np.zeros((self.boardSize,self.boardSize), dtype = int)#list of part of the board that is checked already
        self.captures = [0,0,0]#amount of captured stones
        self.stones = [0,0,0]#amount of stones on the board fo player
        self.currentTurn = 0

    def printBoard(self, board):
        """
            print the given game board with player 1 as x and player w as o
        Parameters
        ----
            board : 2d array with shape boardSize,boardSize
        Returns
        ----
            nothing
        """
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

    def takeTurn(self, coord, player):#TODO should return the resulting board, score and if done
        """
            handles everything that happens during a turn
        Parameters
        ----
            coord : tupple, coord is used as (row,col)
            player: int, number of the player, can be 1 or 2
        Returns
        ----
            nothing
        """
        if(not self.checkValidMove(coord,player)):
            return
        self.currentBoard[coord] = player
        self.stones[player] += 1
        self.resolveTurn(player)
        self.boardHistory = np.vstack((self.boardHistory,np.expand_dims(self.currentBoard,axis=0)))
        self.currentTurn += 1

    def checkNeighbours(self,coord):
        """
            check the neighbours of a coordinate
        Parameters
        ----
            coord : list of tupples, coord is used as (row,col)
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
            coord : tupple, coord is used as (row,col)
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
            coord : tupple, coord is used as (row,col)
            val: int, state of a stone, can be 0, 1 or 2
        Returns
        ----
            list of the full chain
        """
        list1.append(coord)
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
            chain : list of tupple coordinates (row,col)
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
            chain : list of tupple coordinates (row,col)
        Returns
        ----
            nothing
        """
        for coord in chain:
            self.currentBoard[coord] = 0

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
        groups = [],[],[]
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
                self.stones[first_player] -= len(chain)
                self.removeStones(chain)
                capture = True
        for chain in chains[first_player]:
            if(len(self.getLiberties(chain)) == 0):
                self.captures[first_player] += len(chain)
                self.stones[second_player] -= len(chain)
                self.removeStones(chain)
                capture = True
        if capture:
            self.resolveTurn(player)
            return


        # after all chain captures are done try to make groups, by assigning the neutral chains to a player if all of their liberties are of that player
        # use the groups as score


go = GoGame(5)
go.takeTurn((2,1),2)
go.takeTurn((0,0),2)
go.takeTurn((1,1),1)
go.takeTurn((3,1),1)
go.takeTurn((2,0),1)
go.takeTurn((2,2),1)
go.takeTurn((2,3),1)
go.takeTurn((2,4),1)
go.printBoard(go.currentBoard)
# x = go.resolveTurn((0,0),0,[])

# also create non groups

# if all adjacent intersections of a neutral chain belong to one player or are neutral, the chain is theirs