import gromologist as gml
import numpy as np
import plumed
import os


def sensitivity_claculate(topfile, pdbfile, xtcfile, datfile, filedir):
    td = gml.ThermoDiff()
    # this adds all possible NBFIXes to the list of calculated sensitivities:
    td.add_all_sigma_mods(top=topfile,
                          structure=pdbfile, exclude=['OW', 'HW'])
    # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
    hdata = np.loadtxt(datfile)[:, 1]
    td.add_traj(top=topfile, traj=xtcfile, datasets={'helicity': hdata})
    td.run()  # this part will take some time
    # let's find the difference between the binned derivatives for the lower and upper half of the dataset:
    hmin, hmax = np.min(hdata), np.max(hdata)
    hmid = 0.5 * (hmin + hmax)
    td.calc_discrete_derivatives(dataset='helicity', threshold=[hmin, hmid, hmid, hmax])
    for key in td.discrete_free_energy_derivatives.keys():
        print(key, td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][0])

    # this shows the identities of the modifications:
    print([(i.type, str(i)) for i in td.mods])


def helix_calculation(xtcfile, datfile, pdbfile):  #
    print(xtcfile)
    print(datfile)
    print(pdbfile)
    print("plumed driver --mf_xtc " + xtcfile + " --plumed " + datfile + " --pdb " + pdbfile)
    os.system("plumed driver --mf_xtc " + xtcfile + " --plumed " + datfile + " --pdb " + pdbfile)


