#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by hui_zhou@mail.ecust.edu.cn，2019/03/31
# <--Version:1.0.0-->
import numpy as np
from pandas import DataFrame
from matplotlib import pyplot as plt
from functools import wraps

"""
color=['#110141','#01545a','#017351','#03c383','#aad962','#fbbf45','#ef6932','#ed0345','#a12a5e','#710162']
"""

def plot_wrap(func):
	@wraps(func)
	def wrapper(*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		fig=plt.figure(figsize=(9,5))
		#plt.rcParams['savefig.dpi']=200
		#plt.rcParams['figure.dpi']=200
		#plt.rcParams['figure.figsize']=(8.0,6.5)
		plt.title(title,fontsize=18)
		func(*args,**kargs)
		plt.xticks(range(1,2*len(line.columns.values[:-1]),2),line.columns.values[:-1],fontsize=14)
		plt.yticks(fontsize=14)
		plt.xlabel('Reaction coordinate',fontsize=16)
		plt.ylabel('Energy(eV)',fontsize=16)
		#plt.legend(loc='best')
	return wrapper

@plot_wrap
def plot_TS(line):
	"""根据line(DataFrme)中的数据进行过渡态绘图"""
	for lino in range(len(line.index.values)):
		x=[i for i in range(len(line.columns.values[:-1])) if line.iloc[lino:lino+1,i].notnull().values==True]
		y=[line.iloc[lino:lino+1,i].values[0] for i in x]
		x=2*np.array(x)
		color=line.iloc[lino:lino+1,-1].values[0]
		#plt.plot([0.75,1.25],[0,0],color=color,label=line.iloc[lino:lino+1].index.values[0]) #加标签
		plt.plot([x+0.75,x+1.25],[y,y],linewidth=3,color=color)
		plt.plot([x[:-1]+1.25,x[1:]+0.75],[y[:-1],y[1:]],'--',linewidth=0.5,color=color)
		plot_text(x,y,color,lino)

def plot_text(x,y,color,lino):
	for i in range(len(x)-1):
		x_=(x[i]+x[i+1]+2)/2+0.125*(lino+1)*(-1)**lino
		y_=(y[i]+y[i+1])/2+0.005*(-1)**lino
		text='{:.2f}'.format(abs(y[i]-y[i+1]))
		plt.text(x_,y_,text,ha='center',va='center',fontsize=12.5,color=color)

def main():
	plot_TS(line)
	#plt.show()
	plt.savefig('figure.png',dpi=300,bbox_inches='tight')

if __name__ == '__main__':
	"""clean
	CO_O1=[0,-0.33,0.23,-0.37,-1.58,-0.99,'#110141']
	CO_O2=[0,-0.31,0.05,-0.70,-1.60,-1.21,'#01545a']

	CO_O3=[0,-0.19,0.24,-2.48,-2.18,'#110141']
	#index=[name for name in locals().keys() if name.startswith('CO')]
	line=[CO_O3]
	line=DataFrame(line,index=['CO_O3'],columns=['clean','CO','TS',r'$CO_2$',r'$O_v$','color'])
	title=r''


	O3_Ov=[0,-1.54,-1.67,-1.38,-5.19,-4.86,'#110141']
	line=[O3_Ov]
	line=DataFrame(line,index=['O3_Ov'],columns=[r'$O_v$',r'$O_2$*','CO','TS',r'$CO_2$','clean','color'])
	title=r''
	"""
	"""H2O_dis
	OH_Ce1_H_O3=[0,-0.77,-0.53,-1.44,-1.23,-1.95,'#ef6932']
	line=[OH_Ce1_H_O3]
	line=DataFrame(line,index=['OH_Ce1_H_O3'],columns=['clean',r'$H_2O$',r'$TS_{dis}$',r'OH+$H1$',r'$TS_{mig}$',r'$OH+H3$','color'])
	title=r'Energy diagram of $H_2O$ dissociation on clean $CeO_2$(100)'
	"""
	"""1H2O
	O1=[0,None,None,-0.15,0.51,-1.66,-1.09,'#110141']
	O2=[0,None,None,-0.12,0.50,-1.31,-1.08,'#01545a']
	O3=[0,-0.04,0.65,0.41,None,-1.83,-1.70,'#ef6932']
	"""
	"""
	O4=[0,-0.08,0.30,-2.27,-2.16,'#01545a']
	line=[O4]
	line=DataFrame(line,index=['O4'],columns=['IS','CO',r'TS',r'$CO_2$',r'$O_v$','color'])
	title=r''
	"""
	"""
	O4_Ov=[0,-1.43,-1.49,-0.97,-5.06,-4.87,'#01545a']
	line=[O4_Ov]
	line=DataFrame(line,index=['O4_Ov'],columns=[r'$O_v$',r'$O_2*$','CO','TS',r'$CO_2$','IS','color'])
	title=r''
	"""
	#2H2O

	O3=[0,-0.06,0.75,-1.73,-1.64,'#ed0345']
	line=[O3]
	line=DataFrame(line,index=['O3'],columns=['IS','CO','TS',r'$CO_2$',r'$O_v$','color'])
	title=r''

	"""
	clean=[0,-0.19,0.24,-2.48,-2.18,-3.72,-3.85,None,-7.37,-7.04,'#110141']
	#line=[clean]
	#line=DataFrame(line,index=['clean'],columns=['IS','CO','TS',r'$CO_2$',r'$O_v$',r'$O_2$','CO','TS',r'$CO_2$','IS','color'])
	_H2O=[-2.10,-2.15,-1.87,-4.36,-4.26,-5.09,None,None,-8.50,-8.16,'#01545a']
	__H2O=[-3.22,-3.28,None,-5.58,None,None,None,None,None,None,'#ed0345']
	line=[clean,_H2O,__H2O]
	line=DataFrame(line,index=['clean',r'$1H_2O$',r'$2H_2O$'],columns=['IS','CO','TS',r'$CO_2$',r'$O_v$',r'$O_2$','CO','TS',r'$CO_2$','IS','color'])
	title=''
	"""
	main()
























