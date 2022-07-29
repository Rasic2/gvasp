from matplotlib import pyplot as plt

from plot import PlotPES

plotter = PlotPES(height=8)
lines = {
    r'Ca-doped_CH3OH_1': [None, None, None, 0.06, 0.39, -1.51],
    r'Ca-doped_CH3OH_2': [None, None, None, None, None, -2.46, -0.95, -1.66],
    r'Ca-doped': [0, -0.09, 0.75, 0.06, 0.26, -2.46, -1.02, -1.58],
}

models = ['undoped', 'Ca-doped']
suffix = ['', '_CH3OH_1', '_CH3OH_2']
names = [x + y for x in models for y in suffix]

plt.fill_between([0.6, 7], -2.6, 0.9, facecolor='#FFE1E1')
plt.fill_between([7, 11], -2.6, 0.9, facecolor='#E6FFE7')
plt.fill_between([11, 15.4], -2.6, 0.9, facecolor='#E2E2FF')

for name, line in zip(lines.keys(), lines.values()):
    if (name == 'undoped_CH3OH_1' or name == 'Ca-doped_CH3OH_1'):
        plotter.plot(line, '#ed0345')
    elif (name == 'undoped_CH3OH_2' or name == 'Ca-doped_CH3OH_2'):
        plotter.plot(line, '#004370')
    elif (name == 'undoped' or name == 'Ca-doped'):
        plotter.plot(line, '#000000')

plotter.show()
