#!/usr/bin/env python

import numpy as np
from scipy import interpolate
from functools import wraps
from matplotlib import pyplot as plt

def plot_wrapper(func):
	@wraps(func)
	def wrapper(*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=2 #配置线条宽度
		fig=plt.figure(figsize=(9,9))
		func(*args,**kargs)
		plt.xticks([0,1,2,3],[r'$O_1$',r'$O_2$',r'$O_3$',r'$O_t$'],fontsize=14)
		plt.xlim([-0.1,3.1])
		plt.yticks(fontsize=14)
		plt.ylabel('Energy/(eV)',fontsize=16)
		plt.legend(loc='best')
		plt.show()
		#plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')
	return wrapper

def interpolated_plot(x,y,line='-',label='',color=''):
	"""数据拟合函数，返回拟合后的x和y""" #modified at 2019/05/25 DOS数据三次插值拟合
	count=len(x)
	#print(count)
	x_arr=np.array(x)
	y_arr=np.array(y)
	x_new=np.linspace(x_arr.min(),x_arr.max(),count*100)
	#f=interpolate.PchipInterpolator(x_arr,y_arr)
	f=interpolate.interp1d(x_arr,y_arr,kind='linear')
	y_new=f(x_new)
	plt.plot(x_new,y_new,line,label=label,color=color)

@plot_wrapper
def main():
	plt.plot([-1.31,-2.03,-0.87,-0.6],'p',color='#3A7F99')
	interpolated_plot([0,1,2,3],[-1.31,-2.03,-0.87,-0.6],line=':',color='#3A7F99',label=r'$E_{relax}$')
	plt.plot([3.83,4.33,2.21,2.74],'s',color='#F69221')
	interpolated_plot([0,1,2,3],[3.83,4.33,2.21,2.74],line='--',color='#F69221',label=r'$E_{bond}$')
	plt.plot([2.52,2.30,1.34,2.14],'o',color='#FF4923')
	interpolated_plot([0,1,2,3],[2.52,2.30,1.34,2.14],line='-',color='#FF4923',label=r'$E_{form}$')

main()