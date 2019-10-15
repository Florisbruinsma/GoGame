from GoGame import GoGame
import numpy as np
import random
BOARDSIZE = 5                   # Size of the dimensions of the board
total_episodes = 15000          # Total episodes
learning_rate = 0.8             # Learning rate
max_turns = 10                  # Max steps per episode
gamma = 0.95                    # Discounting rate

# Exploration parameters
epsilon = 1.0                   # Exploration rate
max_epsilon = 1.0               # Exploration probability at start
min_epsilon = 0.01              # Minimum exploration probability 
decay_rate = 0.00005              # Exponential decay rate for exploration prob

action_size = BOARDSIZE*BOARDSIZE           #because you can do a potential action on every space of the board
state_size = action_size**3                 #for neutral player 1 or player 2
qtable = np.zeros((state_size, action_size))
print(qtable.shape)

rewards = []
victories = [0,0,0]#draw, p1 win, p2 win
goGame = GoGame(BOARDSIZE)

for episode in range(total_episodes):
    # Reset the environment
    goGame.restartGame(BOARDSIZE)
    state = goGame.getCurrentBoard()
    step = 0
    done = False
    total_rewards = 0

    for step in range(max_turns):
        exp_exp_tradeoff = random.uniform(0, 1)

        ## If random number > greater than epsilon --> exploitation (taking the biggest Q value for this state)
        if exp_exp_tradeoff > epsilon:
            action = np.argmax(qtable[state,:])
            action = goGame.flatMoveToCoord(action)

        # Else doing a random choice --> exploration
        else:
            action = goGame.getRandomMove(1)

        # Take the action and observe the result after the oponent has also taken a turn
        # new_state, score, done = goGame.takeTurn(action,1)
        new_state, score, done = goGame.takeTurn(action,1)

        # new_state, score, done = goGame.takeTurn(goGame.getRandomMove(2),2)#take a random turn for player 2
        goGame.takeTurn(goGame.getRandomMove(2),2)

        reward = score[1]-score[2]
        action = goGame.coordToFlatMove(action)
        if(action>=25):
            print("error_action")
            action = 24
        # Update Q(s,a):= Q(s,a) + lr [R(s,a) + gamma * max Q(s',a') - Q(s,a)]
        # qtable[new_state,:] : all the actions we can take from new state
        qtable[state, action] = qtable[state, action] + learning_rate * (reward + gamma * np.max(qtable[new_state, :]) - qtable[state, action])

        total_rewards += reward

        # Our new state is state
        state = new_state

        # If done (if we're dead) : finish episode
        if done == True:
            break

    # Reduce epsilon (because we need less and less exploration)
    epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_rate*episode)
    rewards.append(total_rewards)
    if(score[1]>score[2]):
        victories[1] += 1
    elif(score[2]>score[1]):
        victories[2] += 1
    else:
        victories[0] += 1
    if(episode%10 == 0):
        print(victories)

print ("Score over time: " +  str(sum(rewards)/total_episodes))
print(qtable)