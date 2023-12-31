import os
from RLforcefield.rlff import system as s
from RLforcefield.rlff import RL_qfunction as qf
from RLforcefield.rlff import visualization as vs
import random

#### System Initialization
parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
n_atoms = 4
global_radius = 5
local_radius = 2
id = 2
grid_step = 0.005
initial_qval = 14
current_location = (global_radius,) * n_atoms
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", id)
qfunc = qf.Q_function(n_atoms, global_radius, local_radius, grid_step=grid_step, initial_qval=initial_qval,
                      initial_location=current_location)
Alpha_gr = 0.03
time_constant = 4.0  # nano-second
run_time = time_constant + 0.5
sensitivity_counter = 1
access_flag = 0  # 0 = full access login,  1 = low access login

### Q-function Initialization
Alpha_qf = 400
Gamma_qf = 0.2
GaussianSigma_first = 10
GaussianSigma = 2
info_dic = {
    'locations': [],
    'next_locations': [],
    'actiontype': [],
    'actionvalues': [],
    'rewards': [],
    'deltas': [],
    'nextQvalues': [],
    'cur_qvals': [],
    'diffs': [],
    'u_weights': [],
    'l_weights': [],
    'sensitivity_list': []
}

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
print(top_sensitive_atoms)
print(gradients)
gradients = [x * -Alpha_gr for x in gradients]
action = qfunc.gradients2action_convertor(gradients)
changes = qfunc.action2changes_convertor(action)
info_dic['sensitivity_list'].append([current_location, gradients])

print(f"gradients: {gradients}")
print(f"actions: {action}")
print(f"changes: {changes}")

vs.init_system_visualization(n_atoms, global_radius, local_radius, gradients, Alpha_gr, Alpha_qf, Gamma_qf,
                             GaussianSigma_first,
                             GaussianSigma, grid_step)

directory = 'it_2'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)

sys = init_sys.systemmodifier(id, atoms=top_sensitive_atoms, parameters="sigma", change=changes,
                              duration_ns=run_time, path=it_path)

reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant, run_time=run_time, sensitivity=0)
data = qfunc.update_weights(id, Alpha=Alpha_qf, Gamma=Gamma_qf, gaussian_sigma=GaussianSigma_first, reward=reward,
                            normalize=True, current_location=current_location)

next_location = tuple(x + y for x, y in zip(current_location, action))
vs.runtime_visualizarion(id, info_dic=info_dic, act_type="Grad", next_location=next_location, actions=action, data=data,
                         reward=reward, it_path=it_path)
current_location = next_location
qf_next_action = data[8]
id = 3

while id < 500:

    directory = f'it_{id}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)

    random_number = random.random()
    print(f"Epsilon Random Number: {random_number}")

    if random_number > 0.3:  ### Walk based on Q-function decision
        next_action = sys.adjust_tuple_to_avoid_negatives(qf_next_action, current_location, global_radius)
        changes = qfunc.action2changes_convertor(next_action)
        action_type = "QF"
        print(f"QF Based Walk with: {changes}")

    elif random_number > 0.1 and random_number <= 0.3:  ### Walk based on Gradient Discent
        do_senstitivity, gradients = sys.should_calculate_sensitivity(current_location=current_location,
                                                                      info_dic=info_dic, threshold=8)
        do_senstitivity = False
        if do_senstitivity:
            sensitivity_counter += 1
            print("previous sensitivity calculations")
            for sublist in info_dic['sensitivity_list']:
                print(f"location: {sublist[0]} -- values: {sublist[1]}")
            print("********  do sensitivity  ********")

            directory = f'sensitivity{sensitivity_counter}_xtc'
            it_path = os.path.join(parent_dir, directory)
            os.mkdir(it_path)

            sys.trajectory_producer(id=0, duration_ns=6.0, path=it_path, plumed_file="plumed_sens.dat")
            sys.helix_reward_calc(xtc=it_path + "/" + f'output_traj0.xtc', dir=it_path, time_constant=time_constant,
                                  run_time=run_time, sensitivity=1)
            os.chdir(it_path)
            helix_atoms = sys.sensitivity_calc(xtc=it_path + "/" + 'output_traj0.xtc',
                                               helicity=it_path + "/" + 'helix_sens.dat',
                                               exclude=['OW', 'HW', 'Cl', 'K'])
            os.chdir('..')
            top_sensitive_atoms, gradients = init_sys.sensitive_atoms(helix_atoms, n_atoms)
            gradients = [x * -Alpha_gr for x in gradients]
            print(f"new gradients: {gradients}")
            info_dic['sensitivity_list'].append([current_location, gradients])
            print("********  Finished sensitivity  ********")
        else:
            print("******** NOT  do sensitivity  ********")
        next_action = qfunc.gradients2action_convertor(gradients)
        next_action = sys.adjust_tuple_to_avoid_negatives(next_action, current_location, global_radius)
        changes = qfunc.action2changes_convertor(next_action)
        action_type = "Grad"
        print(f"Gradients Based Walk with: {changes}")

    else:  #### Walk based on Randomness
        next_action = tuple(random.randint(-local_radius, local_radius) for _ in range(n_atoms))
        next_action = sys.adjust_tuple_to_avoid_negatives(next_action, current_location, global_radius)
        changes = qfunc.action2changes_convertor(next_action)
        action_type = "Rand"
        print(f"Random Based Walk with: {changes}")

    print(f"Chosen Action: {next_action}")
    print(f"Changes: {changes}")
    print("")

    sys = sys.systemmodifier(id=id, atoms=top_sensitive_atoms, parameters="sigma",
                             change=changes, duration_ns=run_time, path=it_path)
    reward = sys.helix_reward_calc(sys.trj, dir=directory, time_constant=time_constant, run_time=run_time,
                                   sensitivity=0)
    data = qfunc.update_weights(id=id, current_location=current_location, Alpha=Alpha_qf, Gamma=Gamma_qf,
                                gaussian_sigma=GaussianSigma, reward=reward,
                                normalize=True)
    next_location = tuple(x + y for x, y in zip(current_location, next_action))
    vs.runtime_visualizarion(id, info_dic=info_dic, act_type=action_type, next_location=next_location, actions=next_action,
                             data=data, reward=reward, it_path=it_path)

    current_location = next_location
    qf_next_action = data[8]
    id = id + 1
