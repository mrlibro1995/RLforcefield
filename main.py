import os

import numpy as np

from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c

parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
init_sys = s.SystemObj("001_top.top", "001_pdb.pdb", 0)
init_cntrl = c.Controller(init_sys)

helicityatoms = init_sys.sensitivity_calc("001_top.top", "001_pdb.pdb", "001_trajectory.xtc", "001_helix.dat",
                                          ['OW', 'HW'])
sensitive_atoms = init_cntrl.sensitive_atoms(helicityatoms, 5)
print(sensitive_atoms)

it = 2
id = 0
alfa = 0.01

for s_atom in sensitive_atoms:
    change_val = alfa * s_atom[1]
    init_cntrl.systemmodifier(id=id, atom=s_atom[0], para="sigma", change=change_val, ns=1)
    id = id + 1

# array = np.array(sensitive_atoms)
# atoms = array[:, 0]
# gradiants = array[:, 1]
# change_vals = alfa * gradiants.astype(float)

# while it >= 0:
# folder adding and management for every iteration
#     it_dir = "iteration" + str(it)
#     it_path = os.path.join(parent_dir, it_dir)
#     os.mkdir(it_path)
#     print("Directory '% s' created" % it_path)

    # init_cntrl.systemmodifier(id=id, atoms=atoms, para="sigma", changes=change_vals, ns=1)
    # it = it - 1
    # id = id + 1


# for s_atom in sensitive_atoms:
#     # folder adding and management for every atom
#     atomic_dir = s_atom[0]
#     atomic_path = os.path.join(parent_dir, atomic_dir)
#     os.mkdir(atomic_path)
#     print("Directory '% s' created" % atomic_dir)
#
#     # loop for every parameter sigma, epsilon, ... (still not implemented)
#
#     equilibrium = 5
#     id = 0
#     while equilibrium > 0:
#         # folder adding and management for every parameter's change
#         change_dir = "sigma_" + str(id)
#         change_path = os.path.join(atomic_path, change_dir)
#         os.mkdir(change_path)
#         print("Directory '% s' created" % change_dir)
#
#         # calculation of the change
#         alfa = 0.01
#         change_val = alfa * s_atom[1]
#         init_cntrl.systemmodifier(id=id, atom=s_atom[0], para="sigma", change=change_val, ns=1, path=change_path)
#
#         id = id + 1
#         equilibrium = equilibrium - 1
