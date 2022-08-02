from QVasp.common.plot import PlotDOS

plotter = PlotDOS(dos_file='DOSCAR-test', pos_file='CONTCAR-test')
plotter.plot(color='#ed0345')
plotter.plot(atoms='Ce', color='#000000', method="output")
plotter.show()
print()
