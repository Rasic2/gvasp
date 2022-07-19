#! /usr/bin/env python

from matplotlib import pyplot as plt

plt.rc('font',family='Times New Roman') #配置全局字体
plt.rcParams['mathtext.default']='regular' #配置数学公式字体
plt.rcParams['lines.linewidth']=3 #配置线条宽度
plt.rcParams['lines.markersize']=9 #配置线条宽度

x=list(range(1,5))
Ev=[1.91,1.08,1.11,1.13]
E_bond=[2.52,2.66,2.13,2.27]
E_relax=[-0.61,-1.59,-1.02,-1.14]

fig=plt.figure(figsize=(6.5,5))
plt.xticks([1,2,3,4],[r'$O^A$',r'$O^B$',r'$O^C$',r'$O^D$'],fontsize=22)
plt.yticks(fontsize=22)
plt.ylabel('Energy(eV)',fontsize=24)

plt.plot(x,Ev,'o-',label=r'$E_v$')
plt.plot(x,E_bond,'^:',label=r'$E_{bond}$')
plt.plot(x,E_relax,'v--',label=r'$E_{relax}$')
plt.legend(loc='best',fontsize=16)
plt.show()
#plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')
