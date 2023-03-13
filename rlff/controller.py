import gromologist as gml
from RLforcefield.rlff.system import SystemObj

class Controller:
    def __init__(self, system: SystemObj):
        self.sys = system

    def systemmodifier(self, id: int, atom: str, change: float = 0.01, ns: int =10 , para: str = "sigma", path: str = "/"):
        topo = gml.Top(self.sys.topo, pdb=self.sys.pdb)
        topo.check_pdb()
        if (para == "sigma"):
            topo.parameters.edit_atomtype(atom, mod_sigma=change)
        print(str(id) + "_" + str(atom) + "_" + str(change))
        topo.save_top(path + "/" + str(id) + ".top")
        topo.pdb.save_pdb(path + "/" + str(id) + ".pdb")
        newsys = SystemObj(path + "/" + str(id) + ".top", path + "/" + str(id) + ".pdb", id)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.num,duration_ns= ns)

    def sensitive_atoms(self, hel_atoms, n_top):
        '''''''''''''''''''''''''''''''''''''''''''''''
        returns back the n_top sensitive values which 
        are calculated in sensitivity_calc function.2
      according to absolute value of the list.
        '''''''''''''''''''''''''''''''''''''''''''''''
        temp = sorted(hel_atoms, key=lambda x: abs(x[1]))
        top_vals = temp[-n_top:]
        return top_vals
