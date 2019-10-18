import objgraph
from GoGame import GoGame
from Model import Model
from Agent import A2CAgent
import numpy as np
import random
import gym
import time
import gc
from tensorflow.keras import backend
from tensorflow.keras import callbacks
# import xdot

EPOCHS = 20
EPISODES = 10
BOARDSIZE = 5
MAXTURNS = (BOARDSIZE*BOARDSIZE)-BOARDSIZE
logdir= "testlog"
tensorboard_callback = callbacks.TensorBoard(logdir, histogram_freq=1)
callbakcs = [tensorboard_callback]


env = GoGame(BOARDSIZE, maxTurn=MAXTURNS)
model = Model(num_actions=env.action_space.n, callbacks=callbakcs)
agent = A2CAgent(model)

for epoch in range(EPOCHS):
    # gc.collect()
    backend.clear_session()
    objgraph.show_growth()
    print("--------------------------------")
    time_start = time.time()
    rewards_history, episode_wins = agent.train(env,max_steps=MAXTURNS,episodes=EPISODES, info=False, info_step=50)
    print("epoch = {:2} | won {:3}/{:3} matches | mean rewards = {:7.2f} | epoch time = {:6.2f} sec".format(epoch, episode_wins.count(1), len(episode_wins), np.mean(rewards_history), (time.time()-time_start)))


"""
TODO
logging like tensorboard
also select the model for player 2, o this as option in env, stand is rand but can add versions of the model
move functions in my class to make it more logical
check if all local scopus use underscores and class scope use camelcase
use the model in the goclass
add coment to everything in class
change the model
add notebook to git
customize train
dubbel check if groups also take oponent pieces for the score



QUESTIONS
local scope variables class cammelcase
random moves ai in goclass or agent
documenting class
keeping up documentation
document return nothing
shoudl i always return something
passmove (-1,-1)?
removing unnescesary functions
private values
"""