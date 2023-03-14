import gromologist as gml
import numpy as np

from RLforcefield.rlff.system import SystemObj


class Controller:
    def __init__(self, system: SystemObj):
        self.sys = system

    def systemmodifier(self, id: int, atom: str, change: float, ns: int = 1, para: str = "sigma",
                       path: str = "/"):
        topo = gml.Top(self.sys.topo, pdb=self.sys.pdb)
        topo.check_pdb()
        # atoms_changes = np.stack((atoms, changes), axis=1)

        # for a_c in atoms_changes:
        if (para == "sigma"):
            topo.parameters.edit_atomtype(atom, mod_sigma= change)
        topo.save_top(str(id) + ".top")
        topo.pdb.save_pdb(str(id) + ".pdb")
        newsys = SystemObj(str(id) + ".top", str(id) + ".pdb", id)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.num, duration_ns=ns, path=path)

    def sensitive_atoms(self, hel_atoms, n_top):
        '''''''''''''''''''''''''''''''''''''''''''''''
        returns back the nsss_top sensitive values which 
        are calculated in sensitivity_calc function.1
        according to absolute value of the list.
        '''''''''''''''''''''''''''''''''''''''''''''''
        temp = sorted(hel_atoms, key=lambda x: abs(x[1]))
        top_vals = temp[-n_top:]
        return top_vals
