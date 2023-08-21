import numpy as np
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from mdtraj.reporters import XTCReporter
from sys import stdout
import os
from parmed import load_file
from parmed import unit as u


def create_trajectory(num, topfilepath, pdbfilepath):

  # If the trajectory exists already then remove it
  trajectory_filename = f'output_traj{num}.xtc'
  chk_filename = f'state_{num}.chk'
  log_filename = f'output_{num}.log'
  checkfile = True if os.path.isfile(trajectory_filename) else False
  if checkfile:
    os.remove(trajectory_filename)
    os.remove(chk_filename)
    os.remove(log_filename)

  top = load_file(topfilepath)
  pdb = load_file(pdbfilepath)
  top.box = pdb.box[:]
  modeller = Modeller(pdb.topology, pdb.positions)
  integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
  integrator.setRandomNumberSeed(num)
  sys = top.createSystem(nonbondedMethod=PME, nonbondedCutoff=1*nanometer, constraints=HBonds)
  barostat = MonteCarloBarostat(1*bar, 300*kelvin, 25)
  sys.addForce(barostat)
  simulation = Simulation(modeller.topology, sys, integrator)
  if os.path.isfile(f'state_{num}.chk'):
    simulation.loadCheckpoint(f'state_{num}.chk')
  else:
    simulation.context.setPositions(modeller.positions)
    print(f"minimizing in {num}")
    simulation.minimizeEnergy(maxIterations=400)
    print(f"minimized in {num}")

  app = True if os.path.isfile(trajectory_filename) else False

  reporter = XTCReporter(trajectory_filename, 5000, append=app)
  simulation.reporters.append(reporter)
  simulation.reporters.append(StateDataReporter(f'output_{num}.log', 500, time=True, potentialEnergy=True, kineticEnergy=True, totalEnergy=True, temperature=True, volume=True, density=True, speed=True))
  while True:
    try:
      for j in range(1, 10000000):
        simulation.step(1000)
        simulation.saveCheckpoint(f'state_{num}.chk')
    except:
      simulation.loadCheckpoint(f'state_{num}.chk')
      continue
