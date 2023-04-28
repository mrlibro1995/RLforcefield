from gym import Env
from gym.spaces import MultiDiscrete, Dict, Box, MultiBinary
import numpy as np
from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c


class ForceFieldEnv(Env):
    def __init__(self, sys, contl, atom_n, para_n):  # for now para_n = 1 and steps = 5
        self.sys = sys
        self.controller = contl
        # Action Space
        self.action_space = MultiDiscrete([5] * atom_n)
        # Observation Space
        self.observation_space = MultiDiscrete([100] * atom_n)
        # Set start temp
        self.state = self.reset()

    def step(self, atoms, path):
        # Using Q_Learning method to evaluate the best action, now is random
        action = self.action_space.sample()
        obs = self.observation_space.sample()
        print(action)
        print(obs)

        # base = 0.01
        # steps = action * base
        # print("These are my steps I should take: ")
        # print(steps)
        # sys = self.controller.systemmodifier_RL(id=1, it=0, atoms=atoms, step=steps, duration_ns=0.01,
        #                                      path=path)
        return 0 #sys
        #
        # # Apply action
        # # 0 -1 = -1 temperature
        # # 1 -1 = 0
        # # 2 -1 = 1 temperature
        # self.state += action - 1
        # # Reduce shower length by 1 second
        #
        # # Calculate reward
        # if self.state >= 37 and self.state <= 39:
        #     reward = 1
        # else:
        #     reward = -1
        #
        #     # Check if shower is done
        # if self.shower_length <= 0:
        #     done = True
        # else:
        #     done = False
        #
        # # Apply temperature noise
        # # self.state += random.randint(-1,1)
        # # Set placeholder for info
        # info = {}

        # Return step information
        # return self.state, reward, done, info

    def render(self):
        # Implement viz
        pass

    def reset(self):
        # Reset shower temperature
        self.state = np.zeros(shape=self.observation_space.shape, dtype=self.observation_space.dtype)
        return self.state
