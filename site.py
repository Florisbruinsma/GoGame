import selenium
from selenium import webdriver
""""
TODO
menu to restart go back a turn change ai
draw grid with buttons
let ai tke a turn after a move
show score next to board
use images for stones
use image for board
be able to go back over the full game length
let ai play against other ai
chose to go first or second
chose board size from 5 to 9
"""
from flask import Flask, flash, redirect, render_template, request, session, abort
from Model import Model
from GoGame import GoGame
import numpy as np

app = Flask(__name__)
ROWS = 5
COLS = 5
WHITE_PLAYER = 1
BLACK_PLAYER = 2
MODEL_NAME = "goGameV2Size5.h5"
AI_TURN = True

def get_flat_board():
    flat_board = []
    for row in range(ROWS):
        for col in range(COLS):
            stone = driver.find_element_by_css_selector("#board5 > div.row > div > div:nth-child({}) > div:nth-child({})".format(row+1,col+1))
            cell = stone.get_attribute("class")
            if(cell == "cell"):
                flat_board.append(0)
            elif(cell == "cell black"):
                flat_board.append(BLACK_PLAYER)
            elif(cell == "cell white"):
                flat_board.append(WHITE_PLAYER)
    return flat_board

@app.route("/")
@app.route("/reset")
def reset():
    return render_template('main_game.html')

@app.route('/background_process_test')
def background_process_test():
    global AI_TURN
    if(AI_TURN):
        AI_TURN = False
        flat_board = get_flat_board()
        action, _ = model.action_value(np.asarray(flat_board)[None, :])
        coord = env.flatMoveToCoord(int(action))
        if (flat_board[int(action)] == 0):
            stone = driver.find_element_by_css_selector("#board5 > div.row > div > div:nth-child({}) > div:nth-child({})".format(coord[0]+1,coord[1]+1))
            stone.click()
            print ("put stone on ({},{})".format(coord[0],coord[1]))
        else:
            print("invalid move ({},{}) passing instead".format(coord[0],coord[1]))
            pass_move = driver.find_element_by_css_selector("#board5 > div.goPlayers > div.stats.white > div.pass")
            pass_move.click()
        return "Nothing"
    else:
        AI_TURN = True
        return "Nothing"


if __name__ == "__main__":
    env = GoGame(5, maxTurns=50)
    model = Model(num_actions=env.action_space.n)
    model.action_value(env.reset()[None, :])
    model.load_weights(MODEL_NAME)
    driver = webdriver.Chrome("C:\\Users\\flori\\Desktop\\q_learning\\go_game\\chromedriver.exe")
    driver.get("http://127.0.0.1:5000")
    app.run()
