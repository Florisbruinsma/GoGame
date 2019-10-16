from GoGame import GoGame
from Model import Model
from Agent import A2CAgent
import numpy as np
import random
import gym

# env = gym.make('CartPole-v0')
env = gym.make('Pong-ram-v0')
model = Model(num_actions=env.action_space.n)

obs = env.reset()
# no feed_dict or tf.Session() needed at all
agent = A2CAgent(model)
rewards_history = agent.train(env,updates=100)
print("Finished training, testing...")
print("%d out of 200" % agent.test(env))