from argparse import ArgumentParser
from math import pi

import matplotlib.pyplot as plt
from openmc.data import ATOMIC_SYMBOL, zam
import openmc.data
import openmc.deplete
import serpentTools

parser = ArgumentParser()
parser.add_argument('nuclide')
args = parser.parse_args()
nuc = args.nuclide
z, a, m = zam(nuc)

# Read OpenMC results ---------------------------------------------------------

# Open results file
results = openmc.deplete.ResultsList.from_hdf5("openmc/depletion_results.h5")

# Obtain K_eff as a function of time
time, keff = results.get_eigenvalue()

# Obtain concentration as a function of time
time, atoms = results.get_atoms('1', nuc)
radius = 0.39218
volume = pi * radius**2
openmc_conc = atoms * 1e-24/volume  # [atoms] [cm^2/b] / [cm^2] = atom/b

# Read Serpent results --------------------------------------------------------

sdata = serpentTools.read('serpent/serpent_input_dep.m')
fuel = sdata['fuel']
serpent_days = fuel.days
serpent_conc = fuel.getValues('days', 'adens', names=f'{ATOMIC_SYMBOL[z]}{a}{"m" if m else ""}')[0]

# Plot results ----------------------------------------------------------------

fig, ax = plt.subplots()
day = 24*60*60
ax.plot(time/day, openmc_conc, 'kx', label=f"{nuc} (OpenMC)")
ax.plot(serpent_days, serpent_conc, 'b-', label=f"{nuc} (Serpent)")
ax.set_xlabel("Time (days)")
ax.set_ylabel("Atom/barn")
ax.legend()
ax.grid(True, which='both')
plt.show()
