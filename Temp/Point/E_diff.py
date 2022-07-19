#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by hui_zhou@mail.ecust.edu.cn
#-->Version:0.0.1<--

from matplotlib import pyplot as plt
from itertools import chain

plt.rc('font',family='Times New Roman') #配置全局字体
plt.rcParams['mathtext.default']='regular' #配置数学公式字体

fig=plt.figure(figsize=(9,6))
plt.xticks(range(5),['clean',r'clean_$O_2$',r'$1H_2O$',r'$1H_2O$_$O_2$',r'$2H_2O$'],fontsize=14)
plt.yticks(fontsize=14)
plt.xlim((-0.5,4.5))
plt.ylabel('E/(eV)',fontsize=16)

IS=[0,-0.2,-2.10,-2.32,-3.39]
CO_2=[-2.48,-3.85,-4.37,-5.95,-5.12]
CO_3=[-3.90,-3.64,-4.76,-5.00,-4.39]
x=list(range(5))

plt.plot(IS,'o',label='IS')
plt.plot(CO_2,'o',label=r'$CO_2$')
plt.plot(CO_3,'o',label=r'$CO_3^{2-}$',color='#017351')
for x,y in zip(x*3,chain(IS,CO_2,CO_3)):
	plt.text(x+0.15,y,'{0:.2f}'.format(y),ha='center',va='center',fontsize=12)

plt.plot([0],[-4.66],'o',color='#017351')
plt.text(0.15,-4.66,'-4.66',ha='center',va='center',fontsize=12)

#plt.plot([1],[-5.19],'o',color='#017351')
#plt.text(1.1,-5.19,'-5.19',ha='center',va='center',fontsize=12)

#x=[2,2];y=[-5.75,-6.05]
#plt.plot(x,y,'o',color='#017351')
#for x,y in zip(x,y):
#	plt.text(x+0.1,y,'{0:.2f}'.format(y),ha='center',va='center',fontsize=12)

plt.legend(loc='best')
plt.savefig('figure.png',dpi=300,bbox_inches='tight')
#plt.show()