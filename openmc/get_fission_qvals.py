from pathlib import Path
import json

import openmc.data
from tqdm import tqdm

###############################################################################
#                   Determine Q values equivalent to Serpent
###############################################################################

# Fixed heating value from Serpent
# See http://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_fissh
heat_u235 = 202.27e6

# Get Q value for U235
endf_dir = Path('/opt/data/endf/endf-b-vii.1/neutrons')
u235 = openmc.data.IncidentNeutron.from_endf(endf_dir / 'n-092_U_235.endf')
q_u235 = u235[18].q_value

# Get Q values for all fissionable nuclides and scale by the ratio of the U235 Q
# value and heating value
serpent_fission_q = {}
for path in tqdm(list(endf_dir.glob('*.endf'))):
    nuc = openmc.data.IncidentNeutron.from_endf(path)
    if nuc.fission_energy is None:
        continue
    q = nuc[18].q_value
    serpent_fission_q[nuc.name] = heat_u235 * q / q_u235

with open('serpent_fissq.json', 'w') as f:
    json.dump(serpent_fission_q, f)
