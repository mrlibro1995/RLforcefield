from system import SystemObj
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

    def sensitive_atoms(self):
        print("hi")
