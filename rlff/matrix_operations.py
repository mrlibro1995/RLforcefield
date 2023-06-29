import numpy as np

def normalize_matrix(arr, normalize):
    if normalize == True:
        arr /= np.sum(arr)
    else:
        min_val = np.min(arr)
        max_val = np.max(arr)
        arr = arr - min_val
        arr /= (max_val - min_val)
    return arr


def recursive_average(lst):
    my_array = np.array(lst)
    average = np.mean(my_array)
    return average


def add2weights(global_weights, local_weights, loc):
    local_weights_array = np.array(local_weights)
    local_radius = int((local_weights_array.shape[0] - 1) / 2)
    global_radius = int((global_weights.shape[0] - 1) / 2)
    local_radius_tuple = (local_radius,) * local_weights_array.ndim
    for idx, value in np.ndenumerate(local_weights):
        local_loc = tuple(x - y for x, y in zip(idx, local_radius_tuple))
        global_loc = tuple(x + y for x, y in zip(loc, local_loc))
        if all(x >= 0 for x in global_loc) and all(x < global_radius * 2 + 1 for x in global_loc):
            global_weights[global_loc] = global_weights[global_loc] + local_weights[idx]
    return global_weights


def operation_matrices_with_location(matrix1, matrix2, location, op):
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

def check_borders(loc, local_radius, globa_radius):
    global_loc_min = [x - local_radius for x in loc]
    global_loc_max = [x + local_radius for x in loc]
    global_loc_min = [value if value >= 0 else 0 for value in global_loc_min]
    global_loc_max = [value if value < globa_radius * 2 + 1 else globa_radius * 2 for value in global_loc_max]
    return global_loc_min, global_loc_max