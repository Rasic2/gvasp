#!/usr/bin/env python
import numpy as np
from matplotlib import pyplot as plt

plt.rc('font',family='Times New Roman') #配置全局字体
plt.rcParams['mathtext.default']='regular' #配置数学公式字体
plt.rcParams['lines.linewidth']=2 #配置线条宽度
plt.rcParams['lines.markersize']=9 #配置线条宽度
bar_width=0.2

fig=plt.figure(figsize=(5,5))

x1=np.array([1,2,3,4])-0.15
x2=np.array([1,2,3])+0.15

y1=np.array([0.98,1.11,0.51,0.42])
y2=np.array([1.79,2.11,0.76,1.07])

z1=np.array([0.77,0.74,0.41])
z2=np.array([2.1,1.29,0.64])

plt.bar(x1,y1,bar_width,label=r'O-t@m')
plt.bar(x1,y2-y1,bar_width,bottom=y1,label='O-t@d')
#plt.plot(x1,y1+y2,color='#FF9427')

plt.bar(x2,z1,bar_width,label=r'$CeO_4$-t@m')
plt.bar(x2,z2-z1,bar_width,bottom=z1,label=r'$CeO_4$@d')
#plt.plot(x2,z1+z2,color='#F5070D')
for x,y in zip(x1,y1):
	if y!=0:
		plt.text(x,y*0.75,y,ha='center',va='top',fontsize=11)

for x,y in zip(x1,y2):
	plt.text(x,y*0.90,'{:.2f}'.format(y),ha='center',va='top',fontsize=11)

for x,y in zip(x2,z1):
	plt.text(x,y*0.75,'{:.2f}'.format(y),ha='center',va='top',fontsize=11)

for x,y in zip(x2,z2):
	plt.text(x,y*0.90,'{:.2f}'.format(y),ha='center',va='top',fontsize=11)

plt.xticks([1,2,3,4],[1,2,3,4],fontsize=14)
plt.xlabel(r'The count of $H_2O$',fontsize=16)
plt.yticks([],fontsize=14)
plt.ylabel(r'$E_{ads}/(eV)$',fontsize=16)
plt.legend(loc='best')
#plt.show()
plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')
