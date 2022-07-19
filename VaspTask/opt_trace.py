#!/usr/bin/env python
#modified at 2019/10/5

import re
import os
import matplotlib
from matplotlib import pyplot as plt

def plot():
	#with open('OUTCAR')as f:
	#	data=f.read()
	data=os.popen("grep 'FORCES:' OUTCAR")
	force=[float(i.split()[4]) for i in data.read().split('\n') if (len(i)!=0)]
	"""
	energy_=re.findall('(?:\w*?):\s*?(?:\d*?)\s*?(-?\d*?\.\d*?E[+-]\d*?)\s*?(?:-?\d*?\.\d*?E[+-]\d*?)\s*?(?:-?\d*?\.\d*?E[+-]\d*?)\s*?\d*?',data)
	energy=[float(item) for item in energy_]
	"""
	x=range(1,len(force)+1)
	y=force
	plt.figure(figsize=(8,6)) #画布大小：800*600像素
	plt.plot(x,y,'o-') #o散点图 -实线 --虚线
	plt.title('Structure Optimize',fontsize=20,fontfamily='Times New Roman')
	plt.xticks(fontsize=14,fontfamily='Times New Roman')
	plt.yticks(fontsize=14,fontfamily='Times New Roman')
	plt.xlabel('Step',fontsize=18,fontfamily='Times New Roman')
	plt.ylabel('Force',fontsize=18,fontfamily='Times New Roman')
	#plt.ylim(0,0.5)
	plt.show()

plot()