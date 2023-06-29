import numpy as np
from scipy.signal import gaussian
import RLforcefield.rlff.matrix_operations as op

def nd_gaussian(sigma, radius, n, normalize):
    nd_gaussian = []
    window_size = radius * 2 + 1
    for i in range(n):
        kernel_1d = gaussian(window_size, sigma)
        kernel_1d = op.normalize_matrix(kernel_1d, False)
        nd_gaussian.append(kernel_1d)

    Gaus = gaussian_multiplier(nd_gaussian, np.ones(shape=(radius * 2 + 1,) * n))
    Gaus = op.normalize_matrix(Gaus, normalize)

    return Gaus


def gaussian_multiplier(ndg, matrix):
    if len(ndg) == matrix.ndim:
        result_array = np.zeros_like(matrix)
        for idx, value in np.ndenumerate(matrix):
            temp = 0
            for dim in range(len(idx)):
                temp = temp + value * ndg[dim][idx[dim]]
            result_array[idx] = temp
    else:
        print("the number of dimensions are not equal")
    return result_array


