import gromologist as gml
import numpy as np

from RLforcefield.rlff.system import SystemObj


class Controller():
    def __init__(self, system: SystemObj):
        self.sys = system

    def systemmodifier_gradient(self, id: int, it: int, atoms: list, change: list, parameters: str,
                                duration_ns: int = 1.0,
                                path: str = "/"):
        topo = gml.Top(self.sys.topo, pdb=self.sys.pdb)
        topo.check_pdb()
        atoms_changes = [[x, y] for x, y in zip(atoms, change)]
        for a_c in atoms_changes:
            if (parameters == "sigma"):
                topo.parameters.edit_atomtype(a_c[0], mod_sigma=a_c[1])
        topo.save_top(path + "/" + str(it) + ".top")
        topo.pdb.save_pdb(path + "/" + str(it) + ".pdb")
        newsys = SystemObj(path + "/" + str(it) + ".top", path + "/" + str(it) + ".pdb", id)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.id, it=it, duration_ns=duration_ns, path=path)
        return newsys

    def systemmodifier_RL(self, id: int, it: int, atoms: list, step: list,
                          duration_ns: int = 1.0,
                          path: str = "/"):
        topo = gml.Top(self.sys.topo, pdb=self.sys.pdb)
        topo.check_pdb()
        nonzero_parameters = [i for i, num in enumerate(step) if num != 0]
        print("Non zero parameters:")
        print(nonzero_parameters)
        for para in nonzero_parameters:
            for atom in atoms:
                if (para == 0): # sigma = 0
                    topo.parameters.edit_atomtype(atom, mod_sigma=step[para])
        topo.save_top(path + "/" + str(it) + ".top")
        topo.pdb.save_pdb(path + "/" + str(it) + ".pdb")
        newsys = SystemObj(path + "/" + str(it) + ".top", path + "/" + str(it) + ".pdb", id)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.id, it=it, duration_ns=duration_ns, path=path)
        return newsys

    def sensitive_atoms(self, hel_atoms, n_top):
        '''''''''''''''''''''''''''''''''''''''''''''''
        returns back the nsss_top sensitive values which 
        are calculated in sensitivity_calc function.1
        according to absolute value of the list.
        '''''''''''''''''''''''''''''''''''''''''''''''
        temp = sorted(hel_atoms, key=lambda x: abs(x[1]))
        top_vals = temp[-n_top:]
        atoms, changes = zip(*top_vals)
        atoms, changes = list(atoms), list(changes)
        changes = changes / np.linalg.norm(changes)

        return atoms, changes
