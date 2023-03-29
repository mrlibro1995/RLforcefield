import os

import numpy as np

from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c

parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
init_sys = s.SystemObj("v2_top.top", "v2_pdb.pdb", 0)
init_cntrl = c.Controller(init_sys)
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
sensitive_atoms = init_cntrl.sensitive_atoms(helicityatoms, 5)
print(sensitive_atoms)

atoms, changes = zip(*sensitive_atoms)
atoms, changes = list(atoms), list(changes)
changes = changes / np.linalg.norm(changes)
alfa = 0.001

changes = [x * -alfa for x in changes]

directory = 'it_0'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
print("Directory '% s' created" % it_path)

sys = init_cntrl.systemmodifier(id=1, it=0, atom=atoms, para="sigma", change=changes, duration_ns=duration_ns,
                                path=it_path)
sys.helicity_calc(sys.trj, dir=directory)
contl = c.Controller(sys)

it = 1
id = 2

while it < 6:
    directory = f'it_{it}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)
    print("Directory '% s' created" % it_path)

    sys = contl.systemmodifier(id=id, it=it, atom=atoms, para="sigma", change=changes, duration_ns=duration_ns,
                               path=it_path)
    sys.helicity_calc(sys.pdb, sys.trj, dir=directory)
    contl = c.Controller(sys)

    id = id + 1
    it = it + 1
