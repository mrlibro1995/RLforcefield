import os
import numpy as np
from RLforcefield.rlff import RL as rl
from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c
import random

parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", 0)
init_contl = c.Controller(init_sys)
duration_ns = 0.01

"""""
This part of code relates to making initial Trajectory for calculating sensitivity

directory = 'sensitivity_xtc'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
init_sys.trajectory_producer("001_top.top", "001_pdb.pdb", 0, 0, 10.0, it_path)
"""""

helicityatoms = init_sys.sensitivity_calc("v2_traj.xtc", "v2_helix.dat",
                                          ['OW', 'HW', 'Cl', 'K'])
atoms, gradients = init_contl.sensitive_atoms(helicityatoms, 5)

alfa = 0.001
gradients = [x * -alfa for x in gradients]

###### RL package
directory = 'it_0'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
print("Directory '% s' created" % it_path)
rlenv = rl.ForceFieldEnv(init_sys, init_contl, len(atoms), 5)
nextstep = rlenv.step(atoms, it_path)
######

# directory = 'it_0'
# it_path = os.path.join(parent_dir, directory)
# os.mkdir(it_path)
# print("Directory '% s' created" % it_path)
#
# sys = init_contl.systemmodifier_gradient(id=1, it=0, atoms=atoms, parameters="sigma", change=gradients,
#                                             duration_ns=duration_ns,
#                                             path=it_path)
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
#     sys = init_contl.systemmodifier_gradient(id=id, it=it, atoms=atoms, parameters="sigma", change=gradients,
#                                            duration_ns=duration_ns,
#                                            path=it_path)
#     print(directory)
#     sys.helicity_calc(sys.trj, dir=directory)
#
#     id = id + 1
#     it = it + 1
