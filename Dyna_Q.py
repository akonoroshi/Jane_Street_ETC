import numpy as np
import pandas as pd
import math

class Dyna_Q:
    def __init__(self, actions, gamma, alpha=0.2):
        self.actions = actions # List
        self.alpha = alpha # Learning rate
        self.gamma = gamma # Discount rate
        self.q_table = pd.DataFrame(colmuns=self.actions) # states x actions
        self.num_act = {act : 0.00001 for act in self.actions} # Avoid division by 0
        self.tc = np.full()

    def add_state(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    np.random.rand(len(self.actions)) * 0.01,
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def choose_action(self, observation, t):
        # Precondition: observation (state) is a dicrete value
        self.add_state(observation)

        # UCB1 (see my notes on kibela)
        max_value = 0
        max_action = None
        for act in self.actions:
            if self.q_table.ix[observation, act] + math.sqrt(2 * math.log(t) / self.num_act[act]) > max_value:
                max_action = act
                max_value = self.q_table.ix[observation, act]
        self.num_act[max_action] = self.num_act[max_action] + 1

        return max_action

    # Happens after choosing action and observing a new state
    def learn(self, s, a, r, s_, num_iter=100):
        self.add_state(s_)
        update_Q(self, s, a, r, s_)

        # Simulation
        for i in range(num_iter):
            state = self.generate_state()
            action = np.random.choice(self.actions)
        

    def update_Q(self, s, a, r, s_):
        q_target = r + self.gamma * self.q_table.ix[s_, :].max()
        self.q_table.ix[s, a] += self.lr * (q_target - self.q_table.ix[s, a])

    def generate_state(self):
        state = 0 # TODO
        self.add_state(state)
        return state