import os
import numpy as np
from RLforcefield.rlff import system as s
import gromologist as gml

parent_dir = "/orozco/projects/ffRNAdev/Milosz/Alireza/rlff"
directory = f'sensitivity_test0'
it_path = os.path.join(parent_dir, directory)
os.chdir(it_path)

id = 0
sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", id)
sys.trajectory_producer("plumed_sens.dat", id, 1.0, it_path)

sys.helix_reward_calc(xtc=it_path + "/" + f'output_traj0.xtc', dir=it_path, time_constant=1.0,
                      run_time=1.0, sensitivity=1)
os.chdir(it_path)
helix_atoms = sys.sensitivity_calc(xtc=it_path + "/" + 'output_traj0.xtc',
                                   helicity=it_path + "/" + 'helix_sens.dat',
                                   exclude=['OW', 'HW', 'Cl', 'K'])
os.chdir('..')
top_sensitive_atoms, gradients = sys.sensitive_atoms(helix_atoms, 4)
print(top_sensitive_atoms)
print(gradients)

print("")
print("#########################################################")
print("########################## 2 ###########################")
print("#########################################################")
print("")

parent_dir = "/orozco/projects/ffRNAdev/Milosz/Alireza/rlff"
directory = f'sensitivity_test1'
it_path = os.path.join(parent_dir, directory)
os.chdir(it_path)

id = 0
sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", id)
sys.trajectory_producer("plumed_sens.dat", id, 1.0, it_path)

sys.helix_reward_calc(xtc=it_path + "/" + f'output_traj0.xtc', dir=it_path, time_constant=1.0,
                      run_time=1.0, sensitivity=1)
os.chdir(it_path)
helix_atoms = sys.sensitivity_calc(xtc=it_path + "/" + 'output_traj0.xtc',
                                   helicity=it_path + "/" + 'helix_sens.dat',
                                   exclude=['OW', 'HW', 'Cl', 'K'])
os.chdir('..')
top_sensitive_atoms, gradients = sys.sensitive_atoms(helix_atoms, 4)
print(top_sensitive_atoms)
print(gradients)
