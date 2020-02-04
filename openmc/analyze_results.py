
import openmc.deplete
import matplotlib.pyplot as plt

###############################################################################
#                    Read depletion calculation results
###############################################################################


# Open results file
results = openmc.deplete.ResultsList.from_hdf5("depletion_results.h5")

# Obtain K_eff as a function of time
time, keff = results.get_eigenvalue()

# Obtain U235 concentration as a function of time
time, n_U235 = results.get_atoms('1', 'U235')

# Obtain Xe135 absorption as a function of time
time, Xe_gam = results.get_reaction_rate('1', 'Xe135', '(n,gamma)')

###############################################################################
#                            Generate plots
###############################################################################

day = 24*60*60
plt.figure()
plt.plot(time/day, keff, label="K-effective")
plt.xlabel("Time (days)")
plt.ylabel("Keff")
plt.show()

plt.figure()
plt.plot(time/day, n_U235, label="U 235")
plt.xlabel("Time (days)")
plt.ylabel("n U5 (-)")
plt.show()

plt.figure()
plt.plot(time/(24*60*60), Xe_gam, label="Xe135 absorption")
plt.xlabel("Time (days)")
plt.ylabel("RR (-)")
plt.show()
plt.close('all')
