import os
from RLforcefield.rlff import system as s
from RLforcefield.rlff import RL_qfunction as qf
import random

#### System Initialization
parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
n_atoms = 4
global_radius = 5
local_radius = 2
id = 2
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", id)
qfunc = qf.Q_function(n_atoms, global_radius, local_radius,grid_step=0.03)
Alpha_gr = 0.01
time_constant = 3.0 #nano-second


### Q-function Initialization
Alpha_qf = 500
Gamma_qf = 0.8
GaussianSigma_first = 10
GaussianSigma = 2

#### Producing Trajectory for sensitivity calculation, Just for the fist time you add a new systemm
# directory = 'sensitivity_xtc'
# it_path = os.path.join(parent_dir, directory)
# os.mkdir(it_path)
# init_sys.trajectory_producer(0, 0, 10.0, it_path)

#### Producing Trajectory for time constant, Just for the fist time you add a new system
# directory = 'time_constant'
# it_path = os.path.join(parent_dir, directory)
# os.mkdir(it_path)
# init_sys.trajectory_producer(id=1, it=0, duration_ns=2.0, path= it_path)

#### Finding the most sensitive atoms (those are performing important role to make system to be helixed
### We can ignore those atoms which give fake information like "CL"
### To calculate correctly, we need to
helix_atoms = init_sys.sensitivity_calc("v2_traj.xtc", "v2_helix.dat",
                                        ['OW', 'HW', 'Cl', 'K'])
top_sensitive_atoms, gradients = init_sys.sensitive_atoms(helix_atoms, n_atoms)
gradients = [x * -Alpha_gr for x in gradients]
print(gradients)
directory = 'it_2'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
print("Directory '% s' created" % it_path)
sys = init_sys.systemmodifier(id, atoms=top_sensitive_atoms, parameters="sigma", change=gradients,
                              duration_ns=time_constant,
                              path=it_path)
reward = sys.helix_reward_calc(sys.trj, dir=directory,time_constant=time_constant)
next_action, info, data = qfunc.update_weights(id, Alpha_qf, Gamma_qf, GaussianSigma_first, reward, normalize=True)
print("Fist movement Completed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
id = 3

while id < 13:

    directory = f'it_{id}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)
    print("Directory '% s' created" % it_path)

    random_number = random.random()

    if random_number > 0.3: ### Walk based on RL decision
        changes = qfunc.action2changes_convertor(next_action)

    elif random_number > 0.1 and random_number <= 0.3:  ### Walk based on Gradient Discent
        next_action = qfunc.gradients2action_convertor(gradients)
        changes = qfunc.action2changes_convertor(next_action)

    else:  ### Walk based on Randomness
        print("Random Walk")
        next_action = (random.randint(-local_radius, local_radius) for _ in range(n_atoms))
        changes = qfunc.action2changes_convertor(next_action)


    print("STILLL RUNNNNING WELLLLLL!!!!!!!!!!!!!!!!!1")
    sys = sys.systemmodifier(id=id, atoms=top_sensitive_atoms, parameters="sigma",
                                      change=changes,
                                      duration_ns=time_constant,
                                      path=it_path)
    reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant)
    qfunc.current_location = tuple(x + y for x, y in zip(qfunc.current_location, next_action))
    next_action, info, data = qfunc.update_weights(id, Alpha_qf, Gamma_qf, GaussianSigma, reward,
                                                    normalize=True)
    id = id + 1

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
