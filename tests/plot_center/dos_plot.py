from gvasp.common.plot import DOSData, PostDOS
from gvasp.main import main

# main(["-d", "band-center", "-j", "center.json", ])

plotter = PostDOS(dos_files=['DOSCAR_ispin'], pos_files=['CONTCAR_ispin'], xlim=[-10, 5], ISPIN=1, lloc='upper left')

selector = {'0': [{'atoms': 1, 'orbitals': ['s'], 'color': '#ed0345', 'method': 'line', 'label': 'Pt-1-s'},
                  ]}

plotter.plot(selector=selector)
# plotter.plot(atoms="Pt", orbitals=["p"], color="#098760")
# plotter.plot(atoms="Pt", orbitals=["d"], color="#66ccff")
plotter.show()
