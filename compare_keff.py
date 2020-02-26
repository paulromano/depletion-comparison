import matplotlib.pyplot as plt
import numpy as np
import openmc.deplete
import serpentTools
from tabulate import tabulate
from uncertainties import unumpy as unp

# Read OpenMC results ---------------------------------------------------------

# Open results file
results = openmc.deplete.ResultsList.from_hdf5("openmc/depletion_results.h5")

# Obtain K_eff as a function of time
time, k = results.get_eigenvalue()
openmc_keff = unp.uarray(k[:, 0], k[:, 1])
days = time/(24*60*60)

# Read Serpent results --------------------------------------------------------

res = serpentTools.read('serpent/serpent_input_res.m')
serpent_days = res.resdata['burnDays'][:, 0]
serpent_keff = unp.uarray(
    res.resdata['absKeff'][:, 0],
    res.resdata['absKeff'][:, 1]
)

# Plot results ----------------------------------------------------------------

# Show tabulation
data = np.vstack((days, serpent_keff, openmc_keff)).T
print(tabulate(data, headers=['Days', 'Serpent', 'OpenMC']))

diff = 1e5*(openmc_keff - serpent_keff)
fig, ax = plt.subplots()
ax.errorbar(days, unp.nominal_values(diff), 2*unp.std_devs(diff), fmt='b.', ecolor='black')
ax.axhline(color='k', linestyle='--')
ax.set_xlabel("Time [days]")
ax.set_ylabel("$k_{OpenMC} - k_{Serpent}$ [pcm]")
ax.grid(True)
plt.savefig('keff_diff.png', bbox_inches='tight')
