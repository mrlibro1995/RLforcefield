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
qfunc = qf.Q_function(n_atoms, global_radius, local_radius, grid_step=0.03)
Alpha_gr = 0.1
time_constant = 0.25  # nano-second
run_time = time_constant + 0.25

### Q-function Initialization
Alpha_qf = 500
Gamma_qf = 0.8
GaussianSigma_first = 10
GaussianSigma = 2
locations_list = []
action_list = []

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

infolist = []
print("############# INITIAL VALUES ###############")
print("")
infolist.append(f"Number of Atoms (Dimensions of the Simulation): {n_atoms}")
infolist.append(f"Global Radius (Changes range in every dimension): {global_radius}")
infolist.append(f"Local Radius: {local_radius}")
infolist.append(f"Gradients: {gradients}")
infolist.append(f"Alpha for Gradients: {Alpha_gr}")
infolist.append(f"Alpha for Q-Function: {Alpha_qf}")
infolist.append(f"Gamma for Q-Function: {Gamma_qf}")
infolist.append(f"Gassian Sigma for first Iteration: {GaussianSigma_first}")
infolist.append(f"Gassian Sigma for next Iterations: {GaussianSigma}")
for i in infolist:
    print(i)
print("")
print("#############################################")
file_name = "info.txt"
with open(file_name, "w") as file:
    # Write each string in a new line
    for string in infolist:
        file.write(string + "\n")

directory = 'it_2'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
sys = init_sys.systemmodifier(id, atoms=top_sensitive_atoms, parameters="sigma", change=gradients,
                              duration_ns=run_time, path=it_path)

reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant, run_time=run_time)
next_action, data, locations_list = qfunc.update_weights(id, Alpha_qf, Gamma_qf, GaussianSigma_first, reward,
                                                         normalize=True)
action_list.append(qfunc.gradients2action_convertor(gradients))
infolist = []
print(f"######## {id} ITERATION RESULT ########")
print("                                        ")
infolist.append(f"Reward: {reward}")
infolist.append(f"Next action suggested by RL: {next_action}")
infolist.append(f"Current Q-value: {data[1]}")
infolist.append(f"Next Q-value: {data[2]}")
infolist.append(f"Diff: {data[3]}")
infolist.append(f"Delta: {data[4]}")
infolist.append(f"Avg Updating Weights: {data[5]}")
infolist.append(f"Avg Local Weights: {data[6]}")
infolist.append(f"Location: {locations_list[-1]}")
infolist.append("List of Locations: ")
for loc in locations_list:
    infolist.append(str(loc))
infolist.append("List of Actions:")
infolist.append(str(action_list))
for i in infolist:
    print(i)
print("                                        ")
print("#############################################")
print("First movement Completed !!!!!")
file_name = it_path + "/info.txt"
with open(file_name, "w") as file:
    for string in infolist:
        file.write(string + "\n")

id = 3
while id < 13:

    directory = f'it_{id}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)

    random_number = random.random()
    print(f"Epsilon Random Number: {random_number}")
    if random_number > 0.3:  ### Walk based on RL decision
        changes = qfunc.action2changes_convertor(next_action)
        print(f"RL Based Walk with: {changes}")

    elif random_number > 0.1 and random_number <= 0.3:  ### Walk based on Gradient Discent
        next_action = qfunc.gradients2action_convertor(gradients)
        changes = qfunc.action2changes_convertor(next_action)
        print(f"Gradients Based Walk with: {changes}")

    else:  ### Walk based on Randomness
        next_action = tuple(random.randint(-local_radius, local_radius) for _ in range(n_atoms))
        changes = qfunc.action2changes_convertor(next_action)
        print(f"Random Based Walk with: {changes}")
    print(f"Chosen Action: {next_action}")
    print("")

    action_list.append(next_action)
    sys = sys.systemmodifier(id=id, atoms=top_sensitive_atoms, parameters="sigma",
                             change=changes, duration_ns=run_time, path=it_path)
    reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant,run_time=run_time)
    qfunc.current_location = tuple(x + y for x, y in zip(qfunc.current_location, next_action))
    next_action, data, locations_list = qfunc.update_weights(id, Alpha_qf, Gamma_qf, GaussianSigma, reward,
                                                             normalize=True)
    infolist = []
    print(f"######## {id} ITERATION RESULT ########")
    print("                                        ")
    infolist.append(f"Reward: {reward}")
    infolist.append(f"Next action suggested by RL:: {next_action}")
    infolist.append(f"Current Q-value: {data[1]}")
    infolist.append(f"Next Q-value: {data[2]}")
    infolist.append(f"Diff: {data[3]}")
    infolist.append(f"Delta: {data[4]}")
    infolist.append(f"Avg Updating Weights: {data[5]}")
    infolist.append(f"Avg Local Weights: {data[6]}")
    infolist.append(f"Location: {locations_list[-1]}")
    infolist.append("List of Locations: ")
    for loc in locations_list:
        infolist.append(str(loc))
    infolist.append("List of Actions:")
    infolist.append(str(action_list))
    for i in infolist:
        print(i)
    print("                                        ")
    print("#############################################")

    file_name = it_path + "/info.txt"
    with open(file_name, "w") as file:
        # Write each string in a new line
        for string in infolist:
            file.write(string + "\n")

    id = id + 1
