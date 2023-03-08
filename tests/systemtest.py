from RLforcefield.rlff import system as s
from RLforcefield.rlff import controller as c

system = s.SystemObj("001_top.top", "001_pdb.pdb",0)
controller = c.Controller(system)

#s.trajectory_producer(s.topo,s.pdb,s.num)
#s.helicity_calc("001_pdb.pdb", "001_trajectory.xtc", "plumed.dat")
#helicityatoms = s.sensitivity_calc("001_top.top","001_pdb.pdb","001_trajectory.xtc","001_helix.dat",['OW', 'HW'])
#sensitive_atoms = c.sensitive_atoms(helicityatoms, 5)
controller.systemmodifier('C', 0.02)

