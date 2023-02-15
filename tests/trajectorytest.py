from RLforcefield.rlff import trajectory, filemanager

#toppath, pdbpath = filemanager.trajectory_file_manager()
toppath = 'samples/001_top.top'
pdbpath = 'samples/001_pdb.pdb'

trajectory.create_trajectory(0, toppath, pdbpath)