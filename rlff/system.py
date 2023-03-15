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


class SystemObj:
    def __init__(self, topo, pdb, num_sample):
        self.topo = topo
        self.pdb = pdb
        self.num = num_sample

    def trajectory_producer(self, topo, pdb, num=0, duration_ns: int = 1, path: str = "/"):
        # If the trajectory exists already then remove it
        trajectory_filename = path + "/" + f'output_traj{num}.xtc'
        chk_filename = path + "/" +  f'state_{num}.chk'
        log_filename = path + "/" + f'output_{num}.log'
        self.trj = trajectory_filename

        checkfile = True if os.path.isfile(trajectory_filename) else False
        if checkfile:
            os.remove(trajectory_filename)
            os.remove(chk_filename)
            os.remove(log_filename)

        top = load_file(topo)
        pdb = load_file(pdb)
        top.box = pdb.box[:]
        modeller = Modeller(pdb.topology, pdb.positions)
        integrator = LangevinIntegrator(300 * kelvin, 1 / picosecond, 0.002 * picoseconds)
        integrator.setRandomNumberSeed(num)
        sys = top.createSystem(nonbondedMethod=PME, nonbondedCutoff=1 * nanometer, constraints=HBonds)
        barostat = MonteCarloBarostat(1 * bar, 300 * kelvin, 25)
        sys.addForce(barostat)
        simulation = Simulation(modeller.topology, sys, integrator)
        if os.path.isfile(chk_filename):
            simulation.loadCheckpoint(chk_filename)
        else:
            simulation.context.setPositions(modeller.positions)
            print(f"minimizing in {num}")
            simulation.minimizeEnergy(maxIterations=400)
            print(f"minimized in {num}")

        app = True if os.path.isfile(trajectory_filename) else False

        reporter = XTCReporter(trajectory_filename, 5000, append=app)
        simulation.reporters.append(reporter)
        simulation.reporters.append(
            StateDataReporter(log_filename, 500, time=True, potentialEnergy=True, kineticEnergy=True,
                              totalEnergy=True, temperature=True, volume=True, density=True, speed=True))

        try:
            for j in range(1, duration_ns * 3):
                simulation.step(1000)
                simulation.saveCheckpoint(chk_filename)
        except:
            simulation.loadCheckpoint(chk_filename)



    def helicity_calc(self, pdb, xtc, plumed):
        command = "plumed driver --mf_xtc " + xtc + " --plumed " + plumed + " --pdb " + pdb
        print(command)
        os.system(command)
        print("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")

    def sensitivity_calc(topfile, top, pdb, xtc, helicity, exclude):

        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            calculation of sensitivity of each atom *
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        td = gml.ThermoDiff()
        # this adds all possible NBFIXes to the list of calculated sensitivities:
        td.add_all_sigma_mods(top=top,
                              structure=pdb, exclude=exclude)
        # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
        hdata = np.loadtxt(helicity)[:, 1]
        td.add_traj(top=top, traj=xtc, datasets={'helicity': hdata})
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
        # print(helix_atoms)
        return hel_by_atom
