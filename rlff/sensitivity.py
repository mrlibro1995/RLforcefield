import gromologist as gml
import numpy as np

def claculate (topfile, pdbfile, xtcfile, datfile):
        td = gml.ThermoDiff()
        # this adds all possible NBFIXes to the list of calculated sensitivities:
        td.add_all_sigma_mods(top='001_top.top',
        structure='001_pdb.pdb', exclude=['OW', 'HW'])
        # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
        hdata = np.loadtxt("001_helix.dat")[:,1]
        td.add_traj(top="001_top.top", traj="001_trajectory.xtc", datasets={'helicity': hdata})
        td.run() # this part will take some time
        # let's find the difference between the binned derivatives for the lower and upper half of the dataset:
        hmin, hmax = np.min(hdata), np.max(hdata)
        hmid = 0.5 * (hmin + hmax)
        td.calc_discrete_derivatives(dataset='helicity', threshold=[hmin, hmid, hmid, hmax])
        for key in td.discrete_free_energy_derivatives.keys():
                print(key, td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][0])

        # this shows the identities of the modifications:
        print([(i.type, str(i)) for i in td.mods])


