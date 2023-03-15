import os

import numpy as np

from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c

parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
init_sys = s.SystemObj("001_top.top", "001_pdb.pdb", 0)
init_cntrl = c.Controller(init_sys)

helicityatoms = init_sys.sensitivity_calc("001_top.top", "001_pdb.pdb", "001_trajectory.xtc", "001_helix.dat",
                                          ['OW', 'HW', 'Cl', 'K'])
sensitive_atoms = init_cntrl.sensitive_atoms(helicityatoms, 5)
print(sensitive_atoms)
atoms, changes = zip(*sensitive_atoms)
atoms, changes = list(atoms), list(changes)

alfa = 0.001

changes = [x * alfa for x in changes]

directory = 'it_0'
it_path = os.path.join(parent_dir, directory)
os.mkdir(it_path)
print("Directory '% s' created" % it_path)
sys = init_cntrl.systemmodifier(id=0, atom=atoms, para="sigma", change=changes, ns=1, path=it_path)
sys.helicity_calc(sys.pdb, sys.trj, dir=directory)
contl = c.Controller(sys)

it = 3
id = 1

while it > 0:
    directory = f'it_{it}'
    it_path = os.path.join(parent_dir, directory)
    os.mkdir(it_path)
    print("Directory '% s' created" % it_path)

    sys = contl.systemmodifier(id=id, atom=atoms, para="sigma", change=changes, ns=1, path=it_path)
    sys.helicity_calc(sys.pdb, sys.trj, 'plumed.dat')
    contl = c.Controller(sys)

    id = id + 1
    it = it - 1
