from RLforcefield.rlff import sensitivity, filemanager

#top_path, pdb_path, xtc_path, dat_path = filemanager.sensitivity_file_manager()
top_path = "samples/001_top.top"
pdb_path = "samples/001_pdb.pdb"
xtc_path = "samples/001_trajectory.xtc"
dat_path = "samples/001_helix.dat"

sensitivity.claculate (top_path, pdb_path, xtc_path, dat_path)