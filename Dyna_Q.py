import numpy as np
import pandas as pd
import math
from operator import add

class Dyna_Q:
    def __init__(self, actions, gamma, alpha=0.2):
        self.actions = actions # List
        self.alpha = alpha # Learning rate
        self.gamma = gamma # Discount rate (close to 0: more immediate reward, 1: more long-term reward)
        self.q_table = pd.DataFrame(columns=self.actions) # states x actions
        self.tc = {} # count of (state, action, state_), used to calculate probability below
        self.t = {} # transition function: probability of seeing state_ given state and action
        self.r = {} # reward function: expected reward of a certain action at a given state

    # If the state is new, add it
    def add_state(self, state):
        if state not in self.q_table.index:
            # Append the new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    np.random.rand(len(self.actions)) * 0.01,
                    index=self.q_table.columns,
                    name=state,
                )
            )

            # Add the new state to T and R
            self.tc[state] = {act : {state_ : 0.00001 for state_ in self.q_table.index} for act in self.actions}
            self.t[state] = {act : {state_ : 1 / len(self.q_table.index) for state_ in self.q_table.index} for act in self.actions}
            self.r[state] = {act : 0 for act in self.actions}
            for state_ in self.q_table.index:
                if state_ == state:
                    break
                for act in self.actions:
                    self.tc[state_][act][state] = 0.00001
                    self.t[state_][act][state] = self.tc[state_][act][state] / sum(self.tc[state_][act].values())
                    self.r[state_][act] = 0


    # Do exploitation and exploration using UCB1 algorithm
    def choose_action(self, observation, c=1):
        # Precondition: observation (state) is a dicrete value
        self.add_state(observation)

        # UCB1
        max_value = 0
        max_action = None
        num_state = sum(sum(self.tc[observation][act].values()) for act in self.actions)
        if num_state < 1: # Prevent log from being negative
            num_state = 1
        for act in self.actions:
            if self.q_table.ix[observation, act] + c * math.sqrt(2 * math.log(num_state) / sum(self.tc[observation][act].values())) > max_value:
                max_action = act
                max_value = self.q_table.ix[observation, act]

        return max_action

    # Happens after choosing action and observing a new state
    def learn(self, s, a, r, s_, num_iter=100):
        # Update model
        self.add_state(s_)
        self.update_Q(s, a, r, s_)
        self.tc[s][a].update({s_ : self.tc[s][a][s_] + 1})
        # self.tc[s][a][s_] += 1
        self.t[s][a].update({s_ : self.tc[s][a][s_] / sum(self.tc[s][a].values())})
        #self.t[s][a][s_] = self.tc[s][a][s_] / sum(self.tc[s][a].values())
        self.r[s].update({a : (1 - self.alpha) * self.r[s][a] + self.alpha * r})
        # self.r[s][a] = (1 - self.alpha) * self.r[s][a] + self.alpha * r

        # Simulation
        for i in range(num_iter):
            # Choose states and actions randomly
            state = np.random.choice(self.q_table.index)
            action = np.random.choice(self.actions)

            # Get a new state and reward according to current functions and update Q
            prob = np.array(list(self.t[state][action].values()))
            prob /= prob.sum() # Normalize
            state_ = np.random.choice(self.q_table.index, p=prob)
            reward = self.r[state][action]
            self.update_Q(state, action, reward, state_)
        

    def update_Q(self, s, a, r, s_):
        q_target = r + self.gamma * self.q_table.ix[s_, :].max()
        self.q_table.ix[s, a] += self.alpha * (q_target - self.q_table.ix[s, a])
