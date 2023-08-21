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
grid_step = 0.005
initial_qval = 2
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", id)
qfunc = qf.Q_function(n_atoms, global_radius, local_radius, grid_step=grid_step, initial_qval=initial_qval)
Alpha_gr = 0.05
time_constant = 0.01  # nano-second
run_time = time_constant

### Q-function Initialization
Alpha_qf = 400
Gamma_qf = 0.2
GaussianSigma_first = 10
GaussianSigma = 2
locations_list = []
action_list = []
reward_list = []
delta_list = []
nextQvalue_list = []
cur_qval_list = []
diff_list = []
u_weight_list = []
l_weight_list = []


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
action_list.append("QF")
l_weight_list.append(data[6])
u_weight_list.append(data[5])
delta_list.append(data[4])
diff_list.append(data[3])
nextQvalue_list.append(data[2])
cur_qval_list.append(data[1])
reward_list.append(reward)
infolist = []
print(f"######## {id} ITERATION RESULT ########")
print("                                        ")
infolist.append(f"Next action suggested by QF: {next_action}")
for idx, loc in enumerate(locations_list):
    infolist.append(
        f"loc: {str(loc)} - rew: {round(reward_list[idx], 2)} - Delta: {delta_list[idx]} - Diff: {diff_list[idx]} - n-qval: {nextQvalue_list[idx]} - o-qval: {cur_qval_list[idx]} - uW: {u_weight_list[idx]} - lW: {l_weight_list[idx]} - Act: {action_list[idx]})

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
while id < 200:

    directory = f'it_{id}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)

    random_number = random.random()
    print(f"Epsilon Random Number: {random_number}")
    if random_number > 0.3:  ### Walk based on RL decision
        next_action = sys.adjust_tuple_to_avoid_negatives(next_action, qfunc.current_location)
        changes = qfunc.action2changes_convertor(next_action)
        action_list.append("QF")
        print(f"QF Based Walk with: {changes}")

    elif random_number > 0.1 and random_number <= 0.3:  ### Walk based on Gradient Discent
        next_action = qfunc.gradients2action_convertor(gradients)
        next_action = sys.adjust_tuple_to_avoid_negatives(next_action, qfunc.current_location)
        changes = qfunc.action2changes_convertor(next_action)
        action_list.append("Grad")
        print(f"Gradients Based Walk with: {changes}")

    else:  ### Walk based on Randomness
        next_action = tuple(random.randint(-local_radius, local_radius) for _ in range(n_atoms))
        next_action = sys.adjust_tuple_to_avoid_negatives(next_action, qfunc.current_location)
        changes = qfunc.action2changes_convertor(next_action)
        action_list.append("Rand")
        print(f"Random Based Walk with: {changes}")
    print(f"Chosen Action: {next_action}")
    print("")

    sys = sys.systemmodifier(id=id, atoms=top_sensitive_atoms, parameters="sigma",
                             change=changes, duration_ns=run_time, path=it_path)
    reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant, run_time=run_time)
    qfunc.current_location = tuple(x + y for x, y in zip(qfunc.current_location, next_action))
    next_action, data, locations_list = qfunc.update_weights(id, Alpha_qf, Gamma_qf, GaussianSigma, reward,
                                                             normalize=True)
    l_weight_list.append(data[6])
    u_weight_list.append(data[5])
    delta_list.append(data[4])
    diff_list.append(data[3])
    nextQvalue_list.append(data[2])
    cur_qval_list.append(data[1])
    reward_list.append(reward)

    infolist = []
    print(f"######## {id} ITERATION RESULT ########")
    print("                                        ")
    infolist.append(f"Next action suggested by RL:: {next_action}")

    for idx, loc in enumerate(locations_list):
        infolist.append(
             f"loc: {str(loc)} - rew: {round(reward_list[idx], 2)} - Delta: {delta_list[idx]} - Diff: {diff_list[idx]} - n-qval: {nextQvalue_list[idx]} - o-qval: {cur_qval_list[idx]} - uW: {u_weight_list[idx]} - lW: {l_weight_list[idx]} - Act:{action_list[idx]}")

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
