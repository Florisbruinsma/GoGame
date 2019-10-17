from GoGame import GoGame
from Model import Model
from Agent import A2CAgent
import numpy as np
import random
import gym
import time
EPOCHS = 10
EPISODES = 20
BOARDSIZE = 5
MAXTURNS = (BOARDSIZE*BOARDSIZE)-BOARDSIZE

env = GoGame(BOARDSIZE, maxTurn=MAXTURNS)

model = Model(num_actions=env.action_space.n)
agent = A2CAgent(model)

for epoch in range(EPOCHS):
    time_start = time.time()
    rewards_history, episode_wins = agent.train(env,max_steps=MAXTURNS,episodes=EPISODES, info=True, info_step=5)
    print("epoch = {:2} | won {:3}/{:3} matches | mean rewards = {:7.2f} | epoch time = {:6.2f} sec".format(epoch, episode_wins.count(1), len(episode_wins), np.mean(rewards_history), (time.time()-time_start)))


"""
TODO
make sure train shows final game score
customize train
make sure the rewards are looked at better
logging like tensorboard
also select the model for player 2
fix ram issues
dubbel check if groups also take oponent pieces for the score
move functions in my class to make it more logical


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