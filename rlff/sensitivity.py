import gromologist as gml
import numpy as np
import os

def helix_calculation(xtcfile, datfile, pdbfile):
    os.system("plumed driver --mf_xtc " + xtcfile + " --plumed " + datfile + " --pdb " + pdbfile)

def sensitivity_calculate(topfile, pdbfile, xtcfile, datfile, filedir, exclude):
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    calculation of sensitivity of each atom 
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    td = gml.ThermoDiff()
    # this adds all possible NBFIXes to the list of calculated sensitivities:
    td.add_all_sigma_mods(top=topfile,
                          structure=pdbfile, exclude=exclude)
    # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
    hdata = np.loadtxt(datfile)[:, 1]
    td.add_traj(top=topfile, traj=xtcfile, datasets={'helicity': hdata})
    td.run()  # this part will take some time
    # let's find the difference between the binned derivatives for the lower and upper half of the dataset:
    hmin, hmax = np.min(hdata), np.max(hdata)
    hmid = 0.5 * (hmin + hmax)
    td.calc_discrete_derivatives(dataset='helicity', threshold=[hmin, hmid, hmid, hmax])
    helix_atoms = []

    for i, key in enumerate(td.discrete_free_energy_derivatives.keys()):
        helix_atoms.append([td.mods[i].type,td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][0] ])
    #print(helix_atoms)
    return helix_atoms #returning list of atoms and their sensitivity with [[C,23.2323],[H, 13.2345],...] format
'''''
    

    for key in td.discrete_free_energy_derivatives.keys():
        #helix_atoms.append([key.type, td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][0]])
        print(key, td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][0])
        #print(td.discrete_free_energy_derivatives[key][1])
    # this shows the identities of the modifications:
    print([(i.type, str(i)) for i in td.mods])
'''''

