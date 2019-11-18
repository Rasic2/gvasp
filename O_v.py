#!/usr/bin/env python

from matplotlib import pyplot as plt

plt.rc('font',family='Times New Roman') #配置全局字体
plt.rcParams['mathtext.default']='regular' #配置数学公式字体
plt.rcParams['lines.linewidth']=3 #配置线条宽度
plt.rcParams['lines.markersize']=9 #配置线条宽度

colors=['#108ABF','#1BAD42','#FF9427','#E53F39']
L1=[2.11,2.05,1.03,None]
L2=[2.50,2.15,1.91,3.08]
L3=[2.93,2.63,2.61,3.02]
L4=[2.95,3.06,2.80,3.46]
L={r'$1^{st}$':L1,r'$2^{nd}$':L2}
x=list(range(1,5))

fig=plt.figure(figsize=(6,3.708))
ax=fig.add_subplot(111)
for label,line,color in zip(L.keys(),L.values(),colors):
	x=[index+1 for index,value in enumerate(line) if value is not None]
	y=[ele for ele in line if ele is not None]
	ax.plot(x,y,'-o',color=color,label=label)
	#plt.gca().add_patch(plt.Rectangle((0.8,min(line)),4,(max(line)-min(line)),color=color,alpha=0.618))

plt.xticks([1,2,3,4],[r'$O^A$',r'$O^B$',r'$O^C$',r'$O^D$'],fontsize=16)
plt.yticks(fontsize=16)
plt.ylabel(r'$E_v$(eV)',fontsize=18)
plt.xlim(0.8,4.2)
plt.ylim([3.2,0.8])
#plt.hlines(3.51,1,4,label='bulk',linestyles='dashed')
plt.legend(loc='best',fontsize=14)
#plt.show()
plt.savefig('/Users/apple/Desktop/figure.svg',dpi=300,format='svg',bbox_inches='tight')
