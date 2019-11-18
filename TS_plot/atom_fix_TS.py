#!/usr/bin/env python
# -*- coding:utf-8 -*-
#绘制固定一个原子的TS图
#created by 周慧，2019/04/30
#modified at 2019/05/04，拟合CINEB最高点数据，PCHIP 分段三次 Hermite 插值
# <--Version:0.1.3-->

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from functools import wraps

def plot_wrap(func):
	@wraps(func)
	def wrapper(*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=2 #配置线条宽度
		fig=plt.figure(figsize=(9,5))
		func(*args,**kargs)
		#plt.xticks([1,2,3,4,5,6],['O2','TS1','O1','TS2','O3','sub-O3'],fontsize=18)
		#plt.xticks([1,2,3,4],['sub-O3','O3','TS','IM'],fontsize=18)
		plt.xticks([1,2,3],['IS','TS','FS'],fontsize=18)
		plt.yticks(fontsize=18)
		plt.ylabel('Energy/(eV)',fontsize=22)
		plt.ylim([-0.29,0.16])
		#plt.show()
		plt.savefig('/Users/apple/Desktop/figure.svg',dpi=300,bbox_inches='tight')
	return wrapper

@plot_wrap
def plot():
	#x=np.array([1,2,3,4,5,6])
	#y=[0,0.29,0.11,0.27,-0.97,-0.09]
	#x=np.array([1,2,3,4])
	#y=[0,-0.88,-0.46,-0.88]
	x=np.array([1,2,3])
	y=[0,0.14,-0.25]
	global count
	count=len(y)
	#x=np.linspace(0,count,num=count)
	x_new=np.linspace(x.min(),x.max(),num=count*100)
	#plt.plot(x,y,'o',color='#01545a')
	for i,j in zip(x,y):
		plt.text(i,j-0.03,'{0:.2f}'.format(j),ha='center',va='bottom',fontsize=16)
	f=interpolate.PchipInterpolator(x,y) #通过最高点拟合
	y_new=f(x_new)
	plt.plot(x_new,y_new)
	#plt.plot([[0.85,1.85,2.85,3.85,4.85,5.85],[1.15,2.15,3.15,4.15,5.15,6.15]],[[0,0.29,0.11,0.27,-0.97,-0.09],[0,0.29,0.11,0.27,-0.97,-0.09]],color='#01545a',linewidth=4)
	#plt.plot([[0.85,1.85,2.85,3.85],[1.15,2.15,3.15,4.15]],[[0,-0.88,-0.46,-0.88],[0,-0.88,-0.46,-0.88]],color='#01545a',linewidth=4)
	plt.plot([[0.85,1.85,2.85],[1.15,2.15,3.15]],[[0,0.14,-0.25],[0,0.14,-0.25]],color='#01545a',linewidth=4)
	#g=interpolate.interp1d(x,y,kind='cubic') #'slinear' 'quadratic'
	#g_new=g(x_new)
	#plt.plot(x_new,g_new)

plot()
