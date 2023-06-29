from gym import Env
from gym.spaces import MultiDiscrete, Dict, Box, MultiBinary
import numpy as np
from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c
import RLforcefield.rlff.matrix_operations as op
import RLforcefield.rlff.gaussian as gs
import RLforcefield.rlff.reward_function as rw
import itertools


def q_value_calculation(global_weights, loc, local_radius, n_dimension, normalize):
    mins, maxs = op.check_borders(loc, local_radius, global_radius)
    gaus = gs.nd_gaussian(3, local_radius, n_dimension, normalize)

    # Process of creating local weights: it needs to be checked if it's not out of bounds
    # and if it is it should be split
    ranges = [(x, y) for x, y in zip(mins, maxs)]
    slices_list = [slice(min, max + 1) for min, max in ranges]
    local_weights = global_weights[tuple(slices_list)]

    local_weights_copy = np.copy(local_weights)
    loc_tuple = tuple(local_radius for _ in range(n_dimension))
    gaus_weights = op.operation_matrices_with_location(local_weights_copy, gaus, loc_tuple, 'mul')
    qval = np.sum(gaus_weights)
    return qval


def update_weights(global_weights, global_qvalues, loc, local_radius, global_radius, Alpha, Gamma, gaussian_sigma,
                   n_dimension, id, average_reward, normalize):
    global_qvalues_copy = np.copy(global_qvalues)
    Gaus = gs.nd_gaussian(gaussian_sigma, local_radius, n_dimension, normalize)

    if id == 0:
        mins, maxs = op.check_borders(loc, local_radius, global_radius)
        factor = global_qvalues[loc] / q_value_calculation(global_weights, loc, local_radius,
                                                                        n_dimension, normalize)
        global_weights = global_weights * factor
    else:
        mins, maxs = op.check_borders(loc, local_radius, global_radius)

    ranges = [(x, y + 1) for x, y in zip(mins, maxs)]
    combinations = list(itertools.product(*[range(r[0], r[1]) for r in ranges]))
    for idx, combination in enumerate(combinations):
        global_qvalues_copy[combination] = q_value_calculation(global_weights, combination, local_radius, n_dimension,
                                                               normalize)

    # Process of creating local qvalues: it needs to be checked if it's not out of bounds
    # and if it is it should be split
    ranges = [(x, y) for x, y in zip(mins, maxs)]
    slices_list = [slice(min, max + 1) for min, max in ranges]
    qvalues_local = global_qvalues_copy[tuple(slices_list)]
    weights_local = global_weights[tuple(slices_list)]

    qvalues_local_copy = np.copy(qvalues_local)
    loc_tuple = tuple(local_radius for _ in range(n_dimension))
    qvalues_local_copy[loc_tuple] = 0.0
    maxQ_index = np.unravel_index(np.argmax(qvalues_local_copy), qvalues_local_copy.shape)
    gamma_maxQ = Gamma * qvalues_local_copy[maxQ_index]
    diff = gamma_maxQ - global_qvalues[loc]
    reward = rw.reward_calculation(average_reward)
    Delta = diff + reward
    weights_update = Alpha * Delta * Gaus
    next_action = tuple(x - y for x, y in zip(maxQ_index, loc_tuple))
    current_qval = global_qvalues[loc]
    next_qval = qvalues_local_copy[maxQ_index]

    global_qvalues = global_qvalues_copy
    global_weights = op.operation_matrices_with_location(global_weights, weights_update, loc, 'sum')

    info = []
    info.append(f"reward: {round(reward, 2)}")
    info.append(f"avg reward: {round(average_reward, 2)}")
    info.append(f"q_val: {round(current_qval, 2)}")
    info.append(f"next q_val: {round(next_qval, 2)}")
    info.append(f"diff: {round(diff, 2)}")
    info.append(f"Delta: {round(Delta, 2)}")

    data = []
    data.append(round(reward, 2))
    data.append(round(average_reward, 2))
    data.append(round(current_qval, 2))
    data.append(round(next_qval, 2))
    data.append(round(diff, 2))
    data.append(round(Delta, 2))
    print("average of updating weights values: " + str(op.recursive_average(weights_update)))
    print("average of local weights: " + str(op.recursive_average(weights_local)))

    return global_weights, global_qvalues, weights_local, next_action, info, data



# class ForceFieldEnv(Env):
#     def __init__(self, sys, contl, atom_n, para_n):  # for now para_n = 1 and steps = 5
#         self.sys = sys
#         self.controller = contl
#         # Action Space
#         self.action_space = MultiDiscrete([5] * atom_n)
#         # Observation Space
#         self.observation_space = MultiDiscrete([100] * atom_n)
#         # Set start temp
#         self.state = self.reset()
#
#     def step(self, action):
        # Using Q_Learning method to evaluate the best action, now is random


        # base = 0.01
        # steps = action * base
        # print("These are my steps I should take: ")
        # print(steps)
        # sys = self.controller.systemmodifier_RL(id=1, it=0, atoms=atoms, step=steps, duration_ns=0.01,
        #                                      path=path)
        # return 0 #sys
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

    # def render(self):
    #     # Implement viz
    #     pass
    #
    # def reset(self):
    #     # Reset shower temperature
    #     self.state = np.zeros(shape=self.observation_space.shape, dtype=self.observation_space.dtype)
    #     return self.state