from RLforcefield.rlff import system

s = system.systemObj("001_top.top", "001_pdb.pdb",0)
#s.trajectory_producer(s.topo,s.pdb,s.num)
#s.helicity_calc("001_pdb.pdb", "001_trajectory.xtc", "plumed.dat")
#helicityatoms = s.sensitivity_calc("001_top.top","001_pdb.pdb","001_trajectory.xtc","001_helix.dat",['OW', 'HW'])
system.systemmodifier(s,'C', 0.02)