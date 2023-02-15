from RLforcefield.rlff import trajectory, filemanager

toppath, pdbpath = filemanager.trajectory_file_manager()
trajectory.create_trajectory(0, toppath, pdbpath)