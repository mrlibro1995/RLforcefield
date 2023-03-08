import gromologist as gml
from RLforcefield.rlff.system import SystemObj

class Controller:
    def __init__(self, system: SystemObj):
        self.sys = system

    def systemmodifier(self, id: int, atom: str, step: float = 0.01, ns: int =10 , attr: str = "sigma"):
        topo = gml.Top(self.sys.topo, pdb=self.sys.pdb)
        topo.check_pdb()
        if (attr == "sigma"):
            topo.parameters.edit_atomtype(atom, mod_sigma=step)
        print(str(id) + "_" + str(atom) + "_" + str(step) + ".top")
        topo.save_top(str(id) + "_" + str(atom) + "_" + str(step) + ".top")
        topo.pdb.save_pdb(str(id) + "_" + str(atom) + "_" + str(step) + ".pdb")
        newsys = SystemObj(str(id) + "_" + str(atom) + "_" + str(step) + ".top", str(id) + "_" + atom + "_" + str(step) + ".pdb", 1)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.num,duration_ns= ns)

    def sensitive_atoms(self, hel_atoms, n_top):
        '''''''''''''''''''''''''''''''''''''''''''''''
        returns back the n_top sensitive values which 
        are calculated in sensitivity_calc function.
        according to absolute value of the list.
        '''''''''''''''''''''''''''''''''''''''''''''''
        temp = sorted(hel_atoms, key=lambda x: abs(x[1]))
        top_vals = temp[-n_top:]
        return top_vals
