import numpy as np
from openmm.app import *
from openmm import *
from simtk.unit import *
from parmed import unit as u
from mdtraj.reporters import XTCReporter
import os
from parmed import load_file

from tkinter.filedialog import askopenfilename

try:
  offs = int(sys.argv[1])
except:
  offs = 0

"""""
  topfile = askopenfilename()
  print(topfile)
  pdbfile = askopenfilename()
  print(pdbfile)
"""""

def run(m):

  top = load_file('/home/alireza/Desktop/myprojects/irbproject/rlff/samples/1_top.top')
  pdb = load_file('/home/alireza/Desktop/myprojects/irbproject/rlff/samples/1_pdb.pdb')
  top.box = pdb.box[:]
  modeller = Modeller(pdb.topology, pdb.positions)

  integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
  integrator.setRandomNumberSeed(m)
  sys = top.createSystem(nonbondedMethod=PME, nonbondedCutoff=1*nanometer, constraints=HBonds)
  barostat = MonteCarloBarostat(1*bar, 300*kelvin, 25)
  sys.addForce(barostat)
  simulation = Simulation(modeller.topology, sys, integrator)
  if os.path.isfile(f'state_{m}.chk'):
    simulation.loadCheckpoint(f'state_{m}.chk')
  else:
    simulation.context.setPositions(modeller.positions)
    print(f"minimizing in {m}")
    simulation.minimizeEnergy(maxIterations=400)
    print(f"minimized in {m}")
  app = True if os.path.isfile(f'output_traj{m}.xtc') else False
  simulation.reporters.append(XTCReporter(f'output_traj{m}.xtc', 5000, append=app))
  simulation.reporters.append(StateDataReporter(f'output_{m}.log', 500, time=True, potentialEnergy=True, kineticEnergy=True, totalEnergy=True, temperature=True, volume=True, density=True, speed=True))
  while True:
    try:
      for j in range(1, 10000000):
        simulation.step(1000)
        simulation.saveCheckpoint(f'state_{m}.chk')
    except:
      simulation.loadCheckpoint(f'state_{m}.chk')
      continue

run(offs)