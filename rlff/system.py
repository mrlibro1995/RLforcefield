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
from openmmplumed import PlumedForce
import scipy.optimize as opt


class SystemObj:
    def __init__(self, topo, pdb, id_sample):
        self.topo = topo
        self.pdb = pdb
        self.id = id_sample
        self.atom_n = 10
        self.para_n = 1

    def trajectory_producer(self,plumed_file = 'plumed_sens.dat', id=0, it=0, duration_ns: float = 1.0, path: str = "/"):
        # If the trajectory exists already then remove it
        trajectory_filename = path + "/" + f'output_traj{it}.xtc'
        chk_filename = path + "/" + f'state_{it}.chk'
        log_filename = path + "/" + f'output_{it}.log'
        self.trj = trajectory_filename

        checkfile = True if os.path.isfile(trajectory_filename) else False
        if checkfile:
            os.remove(trajectory_filename)
            os.remove(chk_filename)
            os.remove(log_filename)

        top = load_file(self.topo)
        pdb = load_file(self.pdb)
        top.box = pdb.box[:]
        modeller = Modeller(pdb.topology, pdb.positions)
        integrator = LangevinIntegrator(300 * kelvin, 1 / picosecond, 0.002 * picoseconds)
        integrator.setRandomNumberSeed(id)
        sys = top.createSystem(nonbondedMethod=PME, nonbondedCutoff=1 * nanometer, constraints=HBonds)
        barostat = MonteCarloBarostat(1 * bar, 300 * kelvin, 25)
        sys.addForce(barostat)
        simulation = Simulation(modeller.topology, sys, integrator)

        if id == 0: # sensitivity calculation
            sys.addForce(PlumedForce(open(plumed_file).read()))
        elif id == 1: # time constant calculation
            sensitivity_path = path.replace('time_constant','sensitivity_xtc')
            sensitivity_checkpoint = sensitivity_path + "/" + f'state_0.chk'
            simulation.loadCheckpoint(sensitivity_checkpoint)
        elif id == 2: # first iteration
            simulation.context.setPositions(modeller.positions)
            print(f"minimizing in {id}")
            simulation.minimizeEnergy(maxIterations=400)
            print(f"minimized in {id}")
        elif id > 2: # second and more iterations, continuing from the already built first trajectory
            previous_path = path.replace(str(it), str(it - 1))
            previous_checkpoint = previous_path + "/" + f'state_{it - 1}.chk'
            simulation.loadCheckpoint(previous_checkpoint)
            print(f"Iteration: {it}")
            print(f"The checkpoint of iteration {it - 1} is loaded")

        app = True if os.path.isfile(trajectory_filename) else False

        reporter = XTCReporter(trajectory_filename, 5000, append=app)
        simulation.reporters.append(reporter)
        simulation.reporters.append(
            StateDataReporter(log_filename, 500, time=True, potentialEnergy=True, kineticEnergy=True,
                              totalEnergy=True, temperature=True, volume=True, density=True, speed=True))
        try:
            loop = int(duration_ns * 500)
            for j in range(1, loop):
                simulation.step(1000)
                simulation.saveCheckpoint(chk_filename)
        except:
            simulation.loadCheckpoint(chk_filename)

    def helicity_calc(self, xtc, dir):
        command = "cp plumed.dat protein.pdb " + dir + "/"
        os.system(command)
        os.chdir(dir)
        print("Current working directory: {0}".format(os.getcwd()))
        command = "plumed driver --mf_xtc " + xtc + " --plumed plumed.dat --pdb " + self.pdb
        os.system(command)
        print("Helicity is calculated by: " + command)
        #self.reward_calculation()
        os.chdir('..')
        print("Finalized working directory: {0}".format(os.getcwd()))

    def reward_calculation(self):
        helix_values = []

        with open('helix.dat', 'r') as file:
            for line in file:
                columns = line.split()
                if len(columns) >= 2:
                    try:
                        value = float(columns[1])
                        helix_values.append(value)
                    except ValueError:
                        pass
        # spliting the list of helicities into 4 sections, you can change 4 to more or less
        helix_splited_lists = self.split_list(helix_values,4)
        x_data = np.array([1, 2, 3, 4])
        helix_splited_averages = [sum(row) / len(row) for row in helix_splited_lists]
        params, _ = opt.curve_fit(a * np.exp(-b * x), x_data, y_data)

    def split_list(lst, n):
        division_length = len(lst) // n
        remainder = len(lst) % n

        sublists = [lst[i * division_length + min(i, remainder):(i + 1) * division_length + min(i + 1, remainder)] for i
                    in range(n)]

        return sublists

    def sensitivity_calc(self, xtc, helicity, exclude):

        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            calculation of sensitivity of each atom **
        """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

        td = gml.ThermoDiff()
        # this adds all possible NBFIXes to the list of calculated sensitivities:
        td.add_all_sigma_mods(top=self.topo,
                              structure=self.pdb, exclude=exclude)
        # this specifies a trajectory on which the sensitivity will be calculated, as well as relevant datasets:
        hdata = np.loadtxt(helicity)[:, 1]
        td.add_traj(top=self.topo, traj=xtc, datasets={'helicity': hdata})
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

    def time_constant_calc(self):