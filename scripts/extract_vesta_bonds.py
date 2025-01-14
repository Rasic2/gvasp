from collections import defaultdict

import yaml

file = '/Applications/VESTA/VESTA.app/Contents/Resources/style.ini'

with open(file, "r") as f:
    content = f.readlines()[15:929]

bonds = [item.split() for item in content]

bonds_dict = defaultdict(dict)
for item in bonds:
    bonds_dict[f'Element {item[1]}'].update({f'Element {item[2]}': float(item[4])})

new_bonds_dict = {}
for key, value in bonds_dict.items():
    new_bonds_dict[key] = {'_default_bonds': None}
    new_bonds_dict[key]['_default_bonds'] = value

bonds_dict = dict(new_bonds_dict)
with open("element.yaml", "w") as f:
    yaml.safe_dump(bonds_dict, f)

pass
