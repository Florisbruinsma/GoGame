'''
Functions
keep track of the history of the board by stacing 1d list afetr each other
convert 1d board to 2d and vice versa
get board 2d
get board 1d
    get the board as a flat list
print board
    how the state of the board drawn so people can understand
initialize game
    reset everything needed and initialize the gzme with a given board size
play move
    give the row and column you want to place on, and 1 or 2 for the player
    return new board state, and if the game is over
play move is possible if
    does not revert the game back to a previous stage
    does not suicide your stone
    is not already ocupied
do after move
    check for captures

variables
all board states that have been as 3d array
current board as a 2d array
amount of captured stones per side


?keep score per turn

'''
import numpy as np
class GoGame:
    def __init__(self, boardsize):
        self.boardsize = boardsize
        self.currentBoard = np.zeros((boardsize,boardsize), dtype = int)
        self.gameHistory = self.currentBoard
        self.gamePieces = {
            'p1' : 0,
            'p2' : 0
        }
        self.expectedScore = {
            'p1' : 0,
            'p2' : 0
        }

    def printBoard(self, board):
        print('\n ',end='')
        for col in range(self.boardsize):
            print(col,end='')
        print('')
        for row in range(self.boardsize):
            print(row,end='')
            for col in range(self.boardsize):
                if(board[row][col] == 0):
                    print('-',end='')
                elif(board[row][col] == 1):
                    print('x',end='')
                elif(board[row][col] == 2):
                    print('o',end='')
            print('')

    def takeTurn(self, coord, player):
        if(not self.checkValidMove(coord,player)):
            return False
        self.executeMove(coord, player)
        self.checkCaptures(coord)# maybe first handle the first capture, might go wrong otherwise
        self.gameHistory = np.dstack((self.gameHistory,self.currentBoard))#TODO not yet working as it should
        # check with go.printBoard(go.gameHistory[:][:][1])

    def executeMove(self, coord, player):
        self.currentBoard[coord] = 1 if player=='p1' else 2

    def checkCaptures(self, coord):
        capturedStone = True
        while capturedStone == True:
            capturedStone = False
            for row in range(self.boardsize):
                for col in range(self.boardsize):
                    if(self.currentBoard[row][col] == 1):
                        neighbours = self.checkNeighbours((row,col))
                        if(not (1 in neighbours or 0 in neighbours)):
                            self.currentBoard[row][col] = 2
                            capturedStone = True
                            continue
                    elif(self.currentBoard[row][col] == 2):
                        neighbours = self.checkNeighbours((row,col))
                        if(not (2 in neighbours or 0 in neighbours)):
                            self.currentBoard[row][col] = 1
                            capturedStone = True
                            continue

    #returns the [up,richt,down,left] neighbour, outside of the field is 3
    def checkNeighbours(self,coord):
        row = coord[0]
        col = coord[1]
        neighbours = []
        # up value
        if(row+1 >= self.boardsize):
            neighbours.append(3)
        else:
            neighbours.append(self.currentBoard[row+1][col])
        # right value
        if(col+1 >= self.boardsize):
            neighbours.append(3)
        else:
            neighbours.append(self.currentBoard[row][col+1])
        # down value
        if(row-1 < 0):
            neighbours.append(3)
        else:
            neighbours.append(self.currentBoard[row-1][col])
        # left value
        if(col-1 < 0):
            neighbours.append(3)
        else:
            neighbours.append(self.currentBoard[row][col-1])
        return neighbours

    def checkValidMove(self,coord, player):
        # check if coord is within bounds
        if(max(coord) >= self.boardsize or min(coord) < 0):
            return False
        # check if position is already filled
        if(self.currentBoard[coord] != 0):
            return False
        neighbours = self.checkNeighbours(coord)
        # check for suicide move
        if(not((player == 'p1' and (1 in neighbours or 0 in neighbours)) or (player == 'p2' and (2 in neighbours or 0 in neighbours)))):
            return False
        return True


go = GoGame(5)
go.takeTurn((2,1),'p2')
go.takeTurn((1,1),'p1')
go.takeTurn((3,1),'p1')
go.takeTurn((2,0),'p1')
go.takeTurn((2,2),'p1')
go.printBoard(go.currentBoard)
go.printBoard(go.gameHistory[:][:][1])