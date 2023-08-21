import numpy as np
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from mdtraj.reporters import XTCReporter
from parmed import load_file
import gromologist as gml
import numpy as np
import os
import time

from RLforcefield.rlff.system import SystemObj


class Controller:
    def __int__(self, sys: SystemObj):
        self.sys = sys

    def systemmodifier(self, atom: str, step: float = 0.01, attr: str = "sigma"):
        topo = gml.Top(sys.topo, pdb=sys.pdb)
        topo.check_pdb()
        if (attr == "sigma"):
            topo.parameters.edit_atomtype(atom, mod_sigma=step)
        topo.save_top("newtopo.top")
        topo.pdb.save_pdb("newpdb.pdb")
        newsys = SystemObj("newtopo.top", "newpdb.pdb", 1)
        newsys.trajectory_producer(newsys.topo, newsys.pdb, newsys.num)

    def sensitive_atoms(self, hel_atoms, n_top):
        '''''''''''''''''''''''''''''''''''''''''''''''
        returns back the n_top sensitive values which 
        are calculated in sensitivity_calc function.
        according to absolute value of the list.
        '''''''''''''''''''''''''''''''''''''''''''''''
        temp = sorted(hel_atoms, key=lambda x: abs(x[1]))
        top_vals = temp[-n_top:]
        return top_vals
