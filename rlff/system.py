import numpy as np
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from mdtraj.reporters import XTCReporter
from parmed import load_file
import gromologist as gml
import numpy as np
import os
from openmmplumed import PlumedForce


class SystemObj:
    def __init__(self, topo, pdb, id_sample):
        self.topo = topo
        self.pdb = pdb
        self.id = id_sample


    def trajectory_producer(self, plumed_file='plumed_sens.dat', id=0, duration_ns: float = 1.0, path: str = "/"):
        # If the trajectory exists already then remove it
        trajectory_filename = path + "/" + f'output_traj{id}.xtc'
        chk_filename = path + "/" + f'state_{id}.chk'
        log_filename = path + "/" + f'output_{id}.log'
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

        if id == 0:  # sensitivity calculation
            print("Trajectory for Sensitivity Calculation Process !!!!")
            sys.addForce(PlumedForce(open(plumed_file).read()))
        elif id == 1:  # time constant calculation
            print("Trajectory for Time Constant Process !!!!")
            print("current directory: " + path)
            sensitivity_path = path.replace('time_constant', 'sensitivity_xtc')
            sensitivity_checkpoint = sensitivity_path + "/" + f'state_0.chk'
            print("new directory: " + sensitivity_checkpoint)
            simulation.loadCheckpoint(sensitivity_checkpoint)
            print("checkpoint loaded")
        elif id == 2:  # first iteration
            print("First Iteration !!!!")
            simulation.context.setPositions(modeller.positions)
            print(f"minimizing in {id}")
            simulation.minimizeEnergy(maxIterations=400)
            print(f"minimized in {id}")
        elif id > 2:  # second and more iterations, continuing from the already built first trajectory
            print(f"{id} Iteration !!!!")
            previous_path = path.replace(str(id), str(id - 1))
            previous_checkpoint = previous_path + "/" + f'state_{id - 1}.chk'
            simulation.loadCheckpoint(previous_checkpoint)
            print(f"Iteration: {id}")
            print(f"The checkpoint of iteration {id - 1} is loaded")

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

    def helix_reward_calc(self, xtc, dir, time_constant):
        ### first part: calculation of helicity and save the helix file
        command = "cp plumed.dat protein.pdb " + dir + "/"
        os.system(command)
        os.chdir(dir)
        print("Current working directory: {0}".format(os.getcwd()))
        command = "plumed driver --mf_xtc " + xtc + " --plumed plumed.dat --pdb " + self.pdb
        os.system(command)
        print("Helicity is calculated by: " + command)
        # self.reward_calculation()
        os.chdir('..')
        print("Finalized working directory: {0}".format(os.getcwd()))

        self.helicity = self.reward_calculation(dir,time_constant)

        return self.helicity

    def time_constant_cal(self):
        directory = './time_constant_helicities'  # Replace with the actual directory path
        file_extension = '.dat'

        # Get the list of files in the directory
        file_names = [file for file in os.listdir(directory) if file.endswith(file_extension)]
        data_lists = []  # List to store the extracted data

        for file_path in file_names:
            data_list = []  # List to store the second column data from each file

            with open(file_path, 'r') as file:
                lines = file.readlines()

                for line in lines:
                    if line.startswith('#'):  # Skip comment lines starting with '#'
                        continue

                    columns = line.split()
                    if len(columns) > 1:
                        data_list.append(float(columns[1]))  # Extract the second column and convert to float

            data_lists.append(data_list)  # Add the data list to the main list

            # Print the extracted data lists
        for i, data_list in enumerate(data_lists):
            print("Data list", i + 1, ":", len(data_list))

        average_list = []

        # Get the length of the lists
        list_length = len(data_lists[0])

        # Iterate over each index
        for i in range(list_length):
            average = sum(data[i] for data in data_lists) / len(data_lists)
            average_list.append(average)

        # Print the combined list
        print(f"average of helicities: {average_list}")
        return None

    def reward_calculation(self, dir,time_constant):
        time_constant = time_constant * 100
        time1 = time_constant + 1.5
        # Get thhe list of files in the directory
        file_names = [file for file in os.listdir(dir) if file == "helix.dat"]
        data_lists = []  # List to store the extracted data
        print(f"file names: {file_names}")
        for file_path in file_names:
            file_path = os.path.join(dir, file_path)
            data_list = []  # List to store the second column data from each file
            print(f"file path: {file_path}")
            with open(file_path, 'r') as file:
                lines = file.readlines()

                for line in lines:
                    if line.startswith('#'):  # Skip comment lines starting with '#'
                        continue

                    columns = line.split()
                    if len(columns) > 1:
                        data_list.append(float(columns[1]))  # Extract the second column and convert to float

            data_lists.append(data_list)  # Add the data list to the main list

            # Print the extracted data lists
        for i, data_list in enumerate(data_lists):
            print("Data list", i + 1, ":", data_list)

        h1_index = data_list[int(time1 - (time1 / 5)):int(time1)]
        h1 = sum(h1_index) / len(h1_index)
        numerator = (h1 - data_list[0])
        denominator = 1 - math.exp(-(time1) / time_constant)
        reward = data_list[0] + numerator / denominator
        return reward

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
        return hel_by_atom

    def systemmodifier(self, id: int, atoms: list, change: list, parameters: str,
                                duration_ns: int = 1.0,
                                path: str = "/"):
        topo = gml.Top(self.topo, pdb=self.pdb)
        topo.check_pdb()
        atoms_changes = [[x, y] for x, y in zip(atoms, change)]
        for a_c in atoms_changes:
            if (parameters == "sigma"):
                topo.parameters.edit_atomtype(a_c[0], mod_sigma=a_c[1])
        topo.save_top(path + "/" + str(id) + ".top")
        topo.pdb.save_pdb(path + "/" + str(id) + ".pdb")
        newsys = SystemObj(path + "/" + str(id) + ".top", path + "/" + str(id) + ".pdb", id)
        newsys.trajectory_producer(id=newsys.id, duration_ns=duration_ns, path=path)
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

