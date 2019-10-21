import tensorflow.keras.losses as kls
import tensorflow.keras.optimizers as ko
import tensorflow as tf
import numpy as np

class A2CAgent:
    def __init__(self, model,lr=0.0007):
        # hyperparameters for loss terms
        self.params = {'value': 0.5, 'entropy': 0.0001, 'gamma': 0.99}
        self.model = model
        self.model.compile(
            optimizer=ko.RMSprop(lr=lr),
            # define separate losses for policy logits and value estimate
            loss=[self._logits_loss, self._value_loss]
        )

    def test(self, env, render=True):
        obs, done, ep_reward = env.reset(), False, 0
        while not done:
            action, _ = self.model.action_value(obs[None, :])
            obs, reward, done, _ = env.step(action)
            ep_reward += reward
            if render:
                env.render()
        return ep_reward

    def train(self, env, max_steps=50, episodes=1000, info=False, info_step=25, winning_factor = 1.5, losing_factor = 0.75):
        done = False
        rewards, actions, values = np.empty((3, 0))

        episode_rewards = [0.0]
        epoch_wins = []
        losses = []
        for episode in range(episodes):
            for step in range(max_steps):
                # observations.append(next_obs.copy())
                if('observations' in locals()):
                    observations = np.vstack((observations , next_obs.copy()))
                else:
                    next_obs = env.reset().astype('float32')
                    observations = next_obs.copy()
                action, value = self.model.action_value(next_obs[None, :])
                actions = np.append(actions, action)
                values = np.append(values, value)

                next_obs, reward, done, _ = env.step(int(action))
                episode_rewards[-1] += reward
                rewards = np.append(rewards, reward)
                if done:
                    episode_rewards.append(0.0)
                    if((env.scores[1]-env.scores[2]) > 0):
                        epoch_wins.append(1)
                        rewards *= winning_factor
                    else:
                        epoch_wins.append(0)
                        rewards *= losing_factor
                    next_obs = env.reset()
                    break

            _, next_value = self.model.action_value(next_obs[None, :])
            returns, advs = self._returns_advantages(rewards, values, next_value)
            # a trick to input actions and advantages through same API
            acts_and_advs = np.concatenate([actions[:, None], advs[:, None]], axis=-1)
            # performs a full training step on the collected batch
            # note: no need to mess around with gradients, Keras API handles it
            losses.append(self.model.train_on_batch(observations, [acts_and_advs, returns]))
            if(episode%info_step == 0 and info==True):
                print("episode = {}".format(episode))
            #reset variables
            rewards, actions, values = np.empty((3, 0))
            del observations
        return episode_rewards, epoch_wins, losses

    def _returns_advantages(self, rewards, values, next_value):
        # next_value is the bootstrap value estimate of a future state (the critic)
        returns = np.append(np.zeros_like(rewards), next_value, axis=-1)
        # returns are calculated as discounted sum of future rewards
        for t in reversed(range(rewards.shape[0])):
            returns[t] = rewards[t] + self.params['gamma'] * returns[t+1]# * (1-dones[t])
        returns = returns[:-1]
        # advantages are returns - baseline, value estimates in our case
        advantages = returns - values
        return returns, advantages

    def _value_loss(self, returns, value):
        # value loss is typically MSE between value estimates and returns
        return self.params['value']*kls.mean_squared_error(returns, value)

    def _logits_loss(self, acts_and_advs, logits):
        # a trick to input actions and advantages through same API
        actions, advantages = tf.split(acts_and_advs, 2, axis=-1)
        # sparse categorical CE loss obj that supports sample_weight arg on call()
        # from_logits argument ensures transformation into normalized probabilities
        weighted_sparse_ce = kls.SparseCategoricalCrossentropy(from_logits=True)
        # policy loss is defined by policy gradients, weighted by advantages
        # note: we only calculate the loss on the actions we've actually taken
        actions = tf.cast(actions, tf.int32)
        policy_loss = weighted_sparse_ce(actions, logits, sample_weight=advantages)
        # entropy loss can be calculated via CE over itself
        entropy_loss = kls.categorical_crossentropy(logits, logits, from_logits=True)
        # here signs are flipped because optimizer minimizes
        return policy_loss - self.params['entropy']*entropy_loss