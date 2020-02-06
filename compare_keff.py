import matplotlib.pyplot as plt
import numpy as np
import openmc.deplete
import serpentTools
from tabulate import tabulate

# Read OpenMC results ---------------------------------------------------------

# Open results file
results = openmc.deplete.ResultsList.from_hdf5("openmc/depletion_results.h5")

# Obtain K_eff as a function of time
time, openmc_keff = results.get_eigenvalue()
openmc_keff = openmc_keff[:, 0]
days = time/(24*60*60)

# Read Serpent results --------------------------------------------------------

res = serpentTools.read('serpent/serpent_input_res.m')
serpent_days = res.resdata['burnDays'][:, 0]
serpent_keff = res.resdata['absKeff'][:, 0]

# Plot results ----------------------------------------------------------------

# Show tabulation
data = np.vstack((days, serpent_keff, openmc_keff)).T
print(tabulate(data, headers=['Days', 'Serpent', 'OpenMC']))

plt.plot(days, openmc_keff, label="OpenMC")
plt.plot(serpent_days, serpent_keff, label="Serpent")
#plt.plot(days, openmc_keff - serpent_keff)
plt.xlabel("Time (days)")
plt.ylabel("keff")
plt.legend()
plt.show()
