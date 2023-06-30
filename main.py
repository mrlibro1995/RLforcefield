import os
from RLforcefield.rlff import RL as rl
from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c
import random

#### Initialization
parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
duration_ns = 0.01

#### Initilization of the System
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", 0)
init_contl = c.Controller(init_sys)

#### Producing Trajectory for sensitivity calculation, Just for the fist time you add a new system
# directory = 'sensitivity_xtc'
# it_path = os.path.join(parent_dir, directory)
# os.mkdir(it_path)
# init_sys.trajectory_producer(0, 0, 10.0, it_path)

#### Producing Trajectory for time constant, Just for the fist time you add a new system
directory = 'time_constant'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
init_sys.trajectory_producer(0, 0, 10.0, it_path)

#### Finding the most sensitive atoms (those are performing important role to make system to be helixed
### We can ignore those atoms which give fake information like "CL"
### To calculate correctly, we need to
# helix_atoms = init_sys.sensitivity_calc("v2_traj.xtc", "v2_helix.dat",
#                                         ['OW', 'HW', 'Cl', 'K'])
# top_sensitive_atoms, gradients = init_contl.sensitive_atoms(helix_atoms, 4)
# alfa = 0.001
# gradients = [x * -alfa for x in gradients]
#
# directory = 'it_0'
# it_path = os.path.join(parent_dir, directory)
# os.mkdir(it_path)
# print("Directory '% s' created" % it_path)
#
# sys = init_contl.systemmodifier_gradient(id=1, it=0, atoms=top_sensitive_atoms, parameters="sigma", change=gradients,
#                                          duration_ns=duration_ns,
#                                          path=it_path)
#
# sys.helicity_calc(sys.trj, dir=directory)
# contl = c.Controller(sys)
#
# it = 1
# id = 2
#
# while it < 6:
#     directory = f'it_{it}'
#     it_path = os.path.join(parent_dir, directory)
#     os.mkdir(it_path)
#     print("Directory '% s' created" % it_path)
#
#     sys = init_contl.systemmodifier_gradient(id=id, it=it, atoms=top_sensitive_atoms, parameters="sigma", change=gradients,
#                                            duration_ns=duration_ns,
#                                            path=it_path)
#     print(directory)
#     sys.helicity_calc(sys.trj, dir=directory)
#
#     id = id + 1
#     it = it + 1




#
# ###### RL package
# # Hyperparameters
# alpha = 0.1
# gamma = 0.6
# epsilon = 0.1
#
# # For plotting metrics
# all_epochs = []
# all_penalties = []
#
# # Instantiation from the Environment
# rlenv = rl.ForceFieldEnv(init_sys, init_contl, len(atoms), 5)
#
# done = False
#
# while not done:
#     if random.uniform(0, 1) < epsilon:
#         action = rlenv.action_space.sample()  # Explore action space
#     else:
#         action = np.argmax(q_table[state])  # Exploit learned values
#
#     next_state, reward, done, info = env.step(action)
#
#     old_value = q_table[state, action]
#     next_max = np.max(q_table[next_state])
#
#     new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
#     q_table[state, action] = new_value
#
#     if reward == -10:
#         penalties += 1
#
#     state = next_state
#     epochs += 1
#
