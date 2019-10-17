from GoGame import GoGame
from Model import Model
from Agent import A2CAgent
import numpy as np
import random
import gym
import time

# env = gym.make('CartPole-v0')
env = GoGame(6)
model = Model(num_actions=env.action_space.n)
# env.observation_space.shape
obs = env.reset()

# no feed_dict or tf.Session() needed at all
agent = A2CAgent(model)

rewards_history = agent.train(env,updates=20, info=False, info_step=50)

"""
TODO
make sure train shows final game score
customize train
make sure the rewards are looked at better
"""