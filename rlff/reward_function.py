import numpy as np
import RLforcefield.rlff.gaussian as gs
import RLforcefield.rlff.matrix_operations as op
import math

def reward_distribution(global_raduce, n_dimension, location_list):
    disribution = np.zeros(shape=(global_raduce * 2 + 1,) * n_dimension)
    for loc in location_list:
        Gaus = gs.nd_gaussian(3, 2, n_dimension, False) * 16
        op.add2weights(disribution, Gaus, loc)
    return disribution


def reward_calculation(avg):
    half_gaussian_list = [2 * math.exp(-(index ** 2) / 36) for index in range(17)]
    variance = half_gaussian_list[int(avg)]
    reward = np.random.uniform(-variance + avg, variance + avg)
    return reward