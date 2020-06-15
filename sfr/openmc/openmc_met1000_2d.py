from math import pi, sqrt
import json
from pathlib import Path

import numpy as np
import openmc
import openmc.deplete

################################################################################
# DIMENSIONS FROM LARGE OXIDE CASE

temperature_fuel = 534 + 273.15         # Table 2.15
temperature_structure = 432.5 + 273.15  # Table 2.15
subassembly_pitch = 16.2471             # Table 2.16
subassembly_duct_outer = 15.8123        # Table 2.16
subassembly_duct_thickness = 0.3966     # Table 2.16
subassembly_duct_inner = subassembly_duct_outer - 2*subassembly_duct_thickness

fuel_radius = 0.3236        # Table 2.16
clad_inner_radius = 0.3236  # Table 2.16
clad_outer_radius = 0.3857  # Table 2.16

pin_pitch = 0.8966  # Table 12 from UAM document

################################################################################
# MATERIALS

# Fuel material from table 2.22
fuel = openmc.Material(name='U-TRU-10Zr', temperature=temperature_fuel)
fuel.add_nuclide('U234', 1.1369e-06)
fuel.add_nuclide('U235', 3.0421e-05)
fuel.add_nuclide('U236', 2.4896e-06)
fuel.add_nuclide('U238', 1.9613e-02)
fuel.add_nuclide('Np237', 4.6686e-05)
fuel.add_nuclide('Pu236', 4.9700e-10)
fuel.add_nuclide('Pu238', 1.1695e-04)
fuel.add_nuclide('Pu239', 2.2076e-03)
fuel.add_nuclide('Pu240', 1.3244e-03)
fuel.add_nuclide('Pu241', 1.9375e-04)
fuel.add_nuclide('Pu242', 2.9277e-04)
fuel.add_nuclide('Am241', 1.0791e-04)
fuel.add_nuclide('Am242_m1', 9.2989e-06)
fuel.add_nuclide('Am243', 1.0017e-04)
fuel.add_nuclide('Cm242', 5.6250e-06)
fuel.add_nuclide('Cm243', 5.4321e-07)
fuel.add_nuclide('Cm244', 6.7240e-05)
fuel.add_nuclide('Cm245', 1.7397e-05)
fuel.add_nuclide('Cm246', 9.2285e-06)
fuel.add_element('Zr', 7.2802e-03)
fuel.add_element('Mo', 9.2873e-04)
fuel.volume = 271 * pi * fuel_radius**2

# Structure and coolant materials from table 2.21
ht9 = openmc.Material(name='HT9')
ht9.add_element('Fe', 6.9715e-02)
ht9.add_element('Ni', 4.2984e-04)
ht9.add_element('Cr', 1.0366e-02)
ht9.add_element('Mn', 4.5921e-04)
ht9.add_element('Mo', 4.9007e-04)

sodium = openmc.Material(name='Na')
sodium.add_element('Na', 2.2272e-02)

materials = openmc.Materials([fuel, ht9, sodium])
materials.export_to_xml()

################################################################################
# GEOMETRY

fuel_outer = openmc.ZCylinder(r=fuel_radius)
clad_outer = openmc.ZCylinder(r=clad_outer_radius)
pin_universe = openmc.model.pin(
    [fuel_outer, clad_outer],
    [fuel, ht9, sodium]
)

na_cell = openmc.Cell(fill=sodium)
na_universe = openmc.Universe(cells=(na_cell,))

lattice = openmc.HexLattice()
lattice.center = (0., 0.)
lattice.pitch = (pin_pitch,)
lattice.orientation = 'x'
lattice.universes = [[pin_universe]]
lattice.universes = [
    [pin_universe for _ in range(max(1, 6*ring_index))]
    for ring_index in reversed(range(10))
]
lattice.outer = na_universe

outer_hex = openmc.model.hexagonal_prism(
    subassembly_pitch / sqrt(3.),
    orientation='x',
    boundary_type='periodic'
)
duct_outer_hex = openmc.model.hexagonal_prism(
    subassembly_duct_outer / sqrt(3.), orientation='x')
duct_inner_hex = openmc.model.hexagonal_prism(
    subassembly_duct_inner / sqrt(3.), orientation='x')

lattice_cell = openmc.Cell(fill=lattice, region=duct_inner_hex)
duct = openmc.Cell(fill=ht9, region=~duct_inner_hex & duct_outer_hex)
outside_duct = openmc.Cell(fill=sodium, region=~duct_outer_hex & outer_hex)

geom = openmc.Geometry([lattice_cell, duct, outside_duct])
geom.export_to_xml()

################################################################################
# SIMULATION SETTINGS

settings = openmc.Settings()
settings.particles = 4_000_000
settings.inactive = 20
settings.batches = 220
settings.statepoint = {'batches': []}
settings.output = {'tallies': False}
settings.temperature = {
    'default': temperature_structure,
    'method': 'interpolation',
}
settings.export_to_xml()

################################################################################
# DEPLETION

cumulative_days = np.linspace(0.0, 360.0, 19)
timesteps = np.diff(cumulative_days)
power = 63143.  # 271 * Average linear power from ANL-AFCI-02, Table II.1-3

# Get Serpent fission Q values
data_path = Path('/home/promano/depletion-comparison/data/depletion')
with (data_path / 'serpent_fissq.json').open() as fh:
    serpent_q = json.load(fh)

# Create depletion operator
chain_file = data_path / 'chain_endfb71_sfr.xml'
op = openmc.deplete.Operator(
    geom, settings, chain_file,
    fission_q=serpent_q,
    fission_yield_mode="average"
)

# Execute depletion using integrator
integrator = openmc.deplete.PredictorIntegrator(
    op, timesteps, power, timestep_units='d')
integrator.integrate()
