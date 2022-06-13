#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 绘制固定一个原子的TS图
# created by 周慧，2019/04/30
# modified at 2019/05/04，拟合CINEB最高点数据，PCHIP 分段三次 Hermite 插值
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
		plt.xticks([1,2,3],['IS','TS','FS'],fontsize=18)
		plt.yticks(fontsize=18)
		plt.ylabel('Energy/(eV)',fontsize=22)
		plt.ylim([-0.29,0.16])
		plt.show()
		#plt.savefig('/Users/apple/Desktop/figure.svg',dpi=300,bbox_inches='tight')
	return wrapper

@plot_wrap
def plot():
	x=np.array([1,2,3])
	y=[0,0.14,-0.25]
	global count
	count=len(y)
	x_new=np.linspace(x.min(),x.max(),num=count*100)
	for i,j in zip(x,y):
		plt.text(i,j-0.03,'{0:.2f}'.format(j),ha='center',va='bottom',fontsize=16)
	f=interpolate.PchipInterpolator(x,y) #通过最高点拟合
	y_new=f(x_new)
	plt.plot(x_new,y_new)
	plt.plot([[0.85,1.85,2.85],[1.15,2.15,3.15]],[[0,0.14,-0.25],[0,0.14,-0.25]],color='#01545a',linewidth=4)
	#g=interpolate.interp1d(x,y,kind='cubic') #'slinear' 'quadratic'

plot()
