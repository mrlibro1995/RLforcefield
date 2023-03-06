from RLforcefield.rlff import system
from RLforcefield.rlff import controller

s = system.SystemObj("001_top.top", "001_pdb.pdb",0)
c = controller.Controller()

s.trajectory_producer(s.topo,s.pdb,s.num)
s.helicity_calc("001_pdb.pdb", "001_trajectory.xtc", "plumed.dat")
helicityatoms = s.sensitivity_calc("001_top.top","001_pdb.pdb","001_trajectory.xtc","001_helix.dat",['OW', 'HW'])
c.sensitive_atoms(helicityatoms, 5)
system.systemmodifier(s,'C', 0.02)

