import os

import numpy as np

from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c

parent_dir = "/home/mrlibro/Desktop/myprojects/irbbarcelona/rlff/RLforcefield"
init_sys = s.SystemObj("001_top.top", "001_pdb.pdb", 0)
init_cntrl = c.Controller(init_sys)

helicityatoms = init_sys.sensitivity_calc("001_top.top", "001_pdb.pdb", "001_trajectory.xtc", "001_helix.dat",
                                          ['OW', 'HW', 'Cl','K'])
sensitive_atoms = init_cntrl.sensitive_atoms(helicityatoms, 5)
print(sensitive_atoms)
atoms, changes = zip(*sensitive_atoms)
atoms, changes = list(atoms), list(changes)

alfa = 0.01

changes = [x * alfa for x in changes]

it = 1
id = 0

while it > 0:
    #change_val = alfa * s_atom[1]
    init_cntrl.systemmodifier(id=id, atom=atoms, para="sigma", change=changes, ns=1)
    id = id + 1
    it = it - 1
