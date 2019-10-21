import objgraph
from GoGame import GoGame
from Model import Model
from Agent import A2CAgent
# from old_agent import A2CAgent
import numpy as np
import random
import gym
import time
import gc
from tensorflow.keras import backend
from tensorflow.keras import callbacks
# import xdot

EPOCHS = 20
EPISODES = 50
BOARDSIZE = 5
LEARNINGRATE = 0.01
MAXTURNS = (BOARDSIZE*BOARDSIZE)-BOARDSIZE
# logdir= "testlog"
# tensorboard_callback = callbacks.TensorBoard(logdir, histogram_freq=1)
# callbacks = [tensorboard_callback]
callbacks = None


env = GoGame(BOARDSIZE, maxTurns=MAXTURNS)
model = Model(num_actions=env.action_space.n, callbacks=callbacks)
model.action_value(env.reset()[None, :])#build the model
model.summary()
agent = A2CAgent(model, lr = LEARNINGRATE)
for epoch in range(EPOCHS):
    # gc.collect()
    backend.clear_session()
    objgraph.show_growth()
    print("--------------------------------")
    time_start = time.time()
    rewards_history, episode_wins, losses = agent.train(env,max_steps=MAXTURNS,episodes=EPISODES, info=False, info_step=50)
    print("epoch = {:2} | won {:3}/{:3} matches | mean rewards = {:7.2f} | mean losses = {:7.2f} | epoch time = {:6.2f} sec".format(epoch, episode_wins.count(1), len(episode_wins), np.mean(rewards_history), np.mean(losses), (time.time()-time_start)))


"""
TODO
make own log
print model
fix tensorboard log
change the model
customize train
dubbel check if groups also take oponent pieces for the score
also select the model for player 2, o this as option in env, stand is rand but can add versions of the model
visualise model
add passmove a scoor (-1,-1)
use the model in the goclass
"""