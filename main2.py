import os
import numpy as np
import gromologist as gml
def sensitivity_calc(xtc, helicity, exclude, topo, pdb):
    td = gml.ThermoDiff()
    # this adds all possible NBFIXes to the list of calculated sensitivities:
    td.add_all_sigma_mods(top=topo,
                          structure=pdb, exclude=exclude)
    # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
    hdata = np.loadtxt(helicity)[:, 1]
    td.add_traj(top=topo, traj=xtc, datasets={'helicity': hdata})
    td.run()  # this part will take some time
    # let's find the difference between the binned derivatives for the lower and upper half of the dataset:
    hmin, hmax = np.min(hdata), np.max(hdata)
    hmid = 0.5 * (hmin + hmax)
    td.calc_discrete_derivatives(dataset='helicity', threshold=[hmin, hmid, hmid, hmax])
    hel_by_atom = []

    for i, key in enumerate(td.discrete_free_energy_derivatives.keys()):
        hel_by_atom.append([td.mods[i].type,
                            td.discrete_free_energy_derivatives[key][1] - td.discrete_free_energy_derivatives[key][
                                0]])
    return hel_by_atom
parent_dir = "/orozco/projects/ffRNAdev/Milosz/Alireza/rlff"
directory = f'sensitivity2_xtc'
it_path = os.path.join(parent_dir, directory)
os.chdir(it_path)
sensitivity_calc(xtc="output_traj0.xtc", helicity="helix_sens.dat",topo="0.top",pdb="0.pdb",exclude=['OW', 'HW', 'Cl', 'K'])
os.chdir('..')


