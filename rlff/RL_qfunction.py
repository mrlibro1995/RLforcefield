from scipy.signal import gaussian
import numpy as np
import itertools


class Q_function:
    def __init__(self, global_dimensions, global_radius, local_radius, grid_step):
        self.global_dimensions = global_dimensions
        self.global_radius = global_radius
        self.local_radius = local_radius
        self.current_location = (self.global_radius,) * self.global_dimensions
        self.global_weights = self._nd_gaussian(10, global_radius, global_dimensions, False)
        self.global_qvalues = np.zeros(shape=(global_radius * 2 + 1,) * global_dimensions)
        self.global_qvalues[self.current_location] = 20
        self.grid_step = grid_step

        self.weights_series = []
        self.local_weights_series = []
        self.info_series = []
        self.q_values_series = []
        self.data_series = [[0] * 6 for _ in range(30)]

    def _nd_gaussian(self, sigma, radius, n, normalize):
        nd_gaussian = []
        window_size = radius * 2 + 1
        for i in range(n):
            kernel_1d = gaussian(window_size, sigma)
            kernel_1d = self._normalize_matrix(kernel_1d, False)
            nd_gaussian.append(kernel_1d)

        Gaus = self._gaussian_multiplier(nd_gaussian, np.ones(shape=(radius * 2 + 1,) * n))
        Gaus = self._normalize_matrix(Gaus, normalize)

        return Gaus

    def _normalize_matrix(self, arr, normalize):
        if normalize == True:
            arr /= np.sum(arr)
        else:
            min_val = np.min(arr)
            max_val = np.max(arr)
            arr = arr - min_val
            arr /= (max_val - min_val)
        return arr

    def _gaussian_multiplier(self, ndg, matrix):
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

    def _check_borders(self, loc):
        global_loc_min = [x - self.local_radius for x in loc]
        global_loc_max = [x + self.local_radius for x in loc]
        global_loc_min = [value if value >= 0 else 0 for value in global_loc_min]
        global_loc_max = [value if value < self.globa_radius * 2 + 1 else self.globa_radius * 2 for value in
                          global_loc_max]
        return global_loc_min, global_loc_max

    def _operation_matrices_with_location(self, matrix1, matrix2, location, op):
        # Get dimensions of the matrices
        shape1 = np.shape(matrix1)
        shape2 = np.shape(matrix2)

        # Calculate the center coordinates of the second matrix
        center = tuple(dim // 2 for dim in shape2)

        # Iterate over the elements of the first matrix
        indices = np.indices(shape1).reshape(len(shape1), -1)
        for index in indices.T:
            # Calculate the corresponding coordinates in the second matrix
            offset = np.subtract(index, location)
            second_matrix_index = tuple(center[i] + offset[i] for i in range(len(shape2)))

            # Check if the corresponding coordinates are within the bounds of the second matrix
            if all(0 <= second_matrix_index[i] < shape2[i] for i in range(len(shape2))):
                # Perform the sum operation
                if op == 'sum':
                    matrix1[tuple(index)] += matrix2[second_matrix_index]
                elif op == 'mul':
                    matrix1[tuple(index)] *= matrix2[second_matrix_index]
                elif op == 'sub':
                    matrix1[tuple(index)] -= matrix2[second_matrix_index]
        return matrix1

    def _recursive_average(self, lst):
        my_array = np.array(lst)
        average = np.mean(my_array)
        return average

    def q_value_calculation(self, normalize):
        mins, maxs = self._check_borders(self.current_location, self.local_radius, self.global_radius)
        gaus = self._nd_gaussian(3, self.local_radius, self.global_dimensions, normalize)

        # Process of creating local weights: it needs to be checked if it's not out of bounds
        # and if it is it should be split
        ranges = [(x, y) for x, y in zip(mins, maxs)]
        slices_list = [slice(min, max + 1) for min, max in ranges]
        local_weights = self.global_weights[tuple(slices_list)]

        local_weights_copy = np.copy(local_weights)
        loc_tuple = tuple(self.local_radius for _ in range(self.global_dimensions))
        gaus_weights = self.operation_matrices_with_location(local_weights_copy, gaus, loc_tuple, 'mul')
        qval = np.sum(gaus_weights)
        return qval

    def update_weights(self, id, Alpha, Gamma, gaussian_sigma, reward, normalize):
        global_qvalues_copy = np.copy(self.global_qvalues)
        Gaus = self._nd_gaussian(gaussian_sigma, self.local_radius, self.global_dimensions, normalize)

        if id == 0:
            mins, maxs = self._check_borders(self.current_location, self.local_radius, self.global_radius)
            factor = self.global_qvalues[self.current_location] / self.q_value_calculation(self.global_weights,
                                                                                           self.current_location,
                                                                                           self.local_radius,
                                                                                           self.global_dimensions, normalize)
            self.global_weights = self.global_weights * factor
        else:
            mins, maxs = self._check_borders(self.current_location, self.local_radius, self.global_radius)

        ranges = [(x, y + 1) for x, y in zip(mins, maxs)]
        combinations = list(itertools.product(*[range(r[0], r[1]) for r in ranges]))
        for idx, combination in enumerate(combinations):
            global_qvalues_copy[combination] = self.q_value_calculation(self.global_weights, combination,
                                                                        self.local_radius,
                                                                        self.global_dimensions,
                                                                        normalize)

        # Process of creating local qvalues: it needs to be checked if it's not out of boundss
        # and if it is it should be split
        ranges = [(x, y) for x, y in zip(mins, maxs)]
        slices_list = [slice(min, max + 1) for min, max in ranges]
        qvalues_local = global_qvalues_copy[tuple(slices_list)]
        weights_local = self.global_weights[tuple(slices_list)]

        qvalues_local_copy = np.copy(qvalues_local)
        loc_tuple = tuple(self.local_radius for _ in range(self.global_dimensions))
        qvalues_local_copy[loc_tuple] = 0.0
        maxQ_index = np.unravel_index(np.argmax(qvalues_local_copy), qvalues_local_copy.shape)
        gamma_maxQ = Gamma * qvalues_local_copy[maxQ_index]
        diff = gamma_maxQ - self.global_qvalues[self.current_location]
        Delta = diff + reward
        weights_update = Alpha * Delta * Gaus
        next_action = tuple(x - y for x, y in zip(maxQ_index, loc_tuple))
        current_qval = self.global_qvalues[self.current_location]
        next_qval = qvalues_local_copy[maxQ_index]

        self.global_qvalues = global_qvalues_copy
        self.global_weights = self._operation_matrices_with_location(self.global_weights, weights_update,
                                                                     self.current_location, 'sum')

        info = []
        info.append(f"reward: {round(reward, 2)}")
        info.append(f"q_val: {round(current_qval, 2)}")
        info.append(f"next q_val: {round(next_qval, 2)}")
        info.append(f"diff: {round(diff, 2)}")
        info.append(f"Delta: {round(Delta, 2)}")

        data = []
        data.append(round(reward, 2))
        data.append(round(current_qval, 2))
        data.append(round(next_qval, 2))
        data.append(round(diff, 2))
        data.append(round(Delta, 2))
        print("average of updating weights values: " + str(self._recursive_average(weights_update)))
        print("average of local weights: " + str(self._recursive_average(weights_local)))

        return next_action, info, data

    def gradients2action_convertor(self, gradients):
        action = [int(x / self.grid_step) for x in gradients]
        return action

    def action2changes_convertor(self, action):
        changes = [x * self.grid_step for x in action]
        return changes
