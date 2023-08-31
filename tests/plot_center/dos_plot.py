from gvasp.common.plot import DOSData
from gvasp.main import main

main(["-d", "band-center", "-j", "center.json", ])

# plotter = PlotDOS(dos_file="DOSCAR", pos_file="CONTCAR", xlim=[-10, 5])
# plotter.plot(atoms="Pt", orbitals=["s"], color="#ed0345")
# plotter.plot(atoms="Pt", orbitals=["p"], color="#098760")
# plotter.plot(atoms="Pt", orbitals=["d"], color="#66ccff")
# plotter.show()
