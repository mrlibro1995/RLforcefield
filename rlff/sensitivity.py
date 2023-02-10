import gromologist as gml
import numpy as np

def claculate ():
        td = gml.ThermoDiff()
        # this adds all possible NBFIXes to the list of calculated sensitivities:
        td.add_all_sigma_mods(top='merged_topology.top',
        structure='minimized_structure.pdb')
        # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
        hdata = np.loadtxt('helix.dat')[:,1]
        td.add_traj(top='merged_topology.top', traj='output_traj1.xtc', datasets={'helicity': hdata})
        td.run() # this part will take some time
        # let's find the difference between the binned derivatives for the lower and upper half of the dataset:
        hmin, hmax = np.min(hdata), np.max(hdata)
        hmid = 0.5 * (hmin + hmax)
        td.calc_discrete_derivatives(dataset='helicity', threshold=[hmin, hmid, hmid, hmax])
