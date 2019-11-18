from collections import defaultdict
import re
from matplotlib import pyplot as plt
from pandas import DataFrame

DATA=defaultdict(list)
Efermi=-1.70887995
with open('EIGENVAL') as f:
	for line in f.readlines():
		pattern_1='^\s*?(\d+)\s*?(\d+)\s*?(\d+)\s*?\n?$'
		pattern_2='^\s*?([+-]?\d*?\.\d*?E[+-]?\d*?)\s*?([+-]?\d*?\.\d*?E[+-]?\d*?)\s*?([+-]?\d*?\.\d*?E[+-]?\d*?)\s*?[+-]?\d*?\.\d*?E[+-]?\d*?\s*?\n?$'
		pattern_3='^\s*?(\d*?)\s*?([+-]?\d*?\.\d*?)\s*?([+-]?\d*?\.\d*?)\s*?\n'
		if re.search(pattern_1,line):
			band_ammount=re.search(pattern_1,line).group(3)
			kpoint_ammount=re.search(pattern_1,line).group(2)
		elif re.findall(pattern_2,line):
			coordinate_x=float(re.findall(pattern_2,line)[0][0])
			coordinate_y=float(re.findall(pattern_2,line)[0][1])
			coordinate_z=float(re.findall(pattern_2,line)[0][2])
			coordinate=(coordinate_x,coordinate_y,coordinate_z)
			for i in range(int(band_ammount)):
				DATA['coordinate'].append(coordinate)
		elif re.findall(pattern_3,line):
			DATA['Band'].append(int(re.findall(pattern_3,line)[0][0]))
			DATA['Energy_up'].append(float(re.findall(pattern_3,line)[0][1])-Efermi)
			DATA['Energy_down'].append(float(re.findall(pattern_3,line)[0][2])-Efermi)
DATA=DataFrame(DATA)
DATA['Energy_averge']=(DATA['Energy_up']+DATA['Energy_down'])/2

plt.figure(figsize=(8,6))
for index,group in DATA.groupby('Band'):
	y=list(group.reindex(columns=['Energy_averge'])['Energy_averge'].values)
	plt.plot(y,'-',linewidth=3)

plt.title('Band Structure',fontsize=20,fontfamily='Times New Roman')
plt.xlim((0,int(kpoint_ammount)-1)) #坐标轴范围
plt.xticks(fontsize=14,fontfamily='Times New Roman') #坐标轴刻度
plt.yticks(fontsize=14,fontfamily='Times New Roman')
plt.xlabel('K-points',fontsize=18,fontfamily='Times New Roman') #坐标轴标签
plt.ylabel('Energy/eV',fontsize=18,fontfamily='Times New Roman')
plt.show()
