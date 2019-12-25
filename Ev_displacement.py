#!/usr/bin/env python

import numpy as np
from functools import wraps
from collections import Counter
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
from matplotlib.legend_handler import HandlerLine2D, HandlerTuple
from pandas import DataFrame
from scipy import interpolate
#import statsmodels.api as sm
#import rpy2.robjects as robjects
#from rpy2.robjects import FloatVector
#from rpy2.robjects.packages import importr

def plot_wrapper(func):
	@wraps(func)
	def wrapper(*args,**kargs):
		#plt.rcParams['text.usetex']=True
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=3 #配置线条宽度
		plt.rcParams['lines.markersize']=7 #配置标记大小
		func(*args,**kargs)
		plt.show()
		#plt.savefig('/Users/apple/Desktop/figure.svg',dpi=300,bbox_inches='tight')
	return wrapper

def interpolated_plot(x,y,label='',color=''):
	"""数据拟合函数，返回拟合后的x和y""" #modified at 2019/05/25 DOS数据三次插值拟合
	count=len(x)
	x_arr=np.array(x)
	y_arr=np.array(y)
	x_new=np.linspace(x_arr.min(),x_arr.max(),count*100)
	f=interpolate.PchipInterpolator(x_arr,y_arr)
	#f=interpolate.interp1d(x_arr,y_arr,kind='cubic')
	y_new=f(x_new)
	plt.plot(x_new,y_new,label=label,color=color)

def r_ols(x,y):
	"""调用R lm函数进行OLS回归分析"""
	stats=importr('stats') #载入stats包
	base=importr('base') #载入base包
	robjects.globalenv['r_x']=FloatVector(x) #将nunmpy数组转化为R浮点向量并设置R变量环境
	robjects.globalenv['r_y']=FloatVector(y)
	r_fit=stats.lm('r_y ~ r_x') #调用R lm函数进行线性回归
	r_summary=base.summary(r_fit) #OLS回归拟合结果，返回ListVector
	r_coefficients=list(dict(zip(r_summary.names,[ele for ele in list(r_summary)]))['coefficients']) #获取截距、斜率值
	r_R2=list(dict(zip(r_summary.names,[ele for ele in list(r_summary)]))['r.squared'])[0] #将ListVector先转化为字典并获取R2值，返回FloatVector对象，再将其转化为列表并取值
	r_adj_R2=list(dict(zip(r_summary.names,[ele for ele in list(r_summary)]))['adj.r.squared'])[0]
	symbol='+' if r_coefficients[0] > 0 else "-"
	print("拟合方程为: y = {:.2f}x {} {:.2f} ".format(r_coefficients[1],symbol,abs(r_coefficients[0])))
	print('       R2: {:.4f}\n'.format(r_R2)+'   Adj.R2: {:.4f}\n'.format(r_adj_R2))

def sm_ols(x,y):
	"""statsmodels OLS模型"""
	X=sm.add_constant(x)
	fit=sm.OLS(y,X).fit()
	print(fit.summary())

@plot_wrapper
def main():
	colors=['#000000','#01545a','#ed0345','#ef6932']
	#labels=[r'$O^A$',r'$O^B$',r'$O^C$',r'$O^D$']
	#labels=[r'clean  O-t',r'hydro O-t',r'clean  $CeO_4$-t',r'hydro $CeO_4$-t']
	labels=[r'clean  surface',r'hydro surface',r'clean  surface',r'hydro surface']
	x=np.array([1.91,1.08,0.89,1.13]) #空穴形成能
	y=np.array([0.70,0.58,0.18,0.25]) #barrier1
	z=np.array([0.85,0.60,0.26,0.50]) #barrier2

	x_fit=np.array([1.91,1.08,0.89,1.13])
	y_fit=np.array([0.70,0.58,0.18,0.25])
	z_fit=np.array([0.85,0.60,0.26,0.50])

	fig=plt.figure(figsize=(8,6))
	#plt.subplots_adjust(wspace=0.5)
	ax1=fig.add_subplot(111)
	markers=['o','o','o','o']
	fill_styles=['full','none','full','none']
	points_1=[]
	points_2=[]
	for x_,y_,z_,marker,fill_style,label in zip(x,y,z,markers,fill_styles,labels):
		points_1.append(ax1.plot(x_,y_,marker,fillstyle=fill_style,color='#01545a',label=label))
		points_2.append(ax1.plot(x_,z_,marker,fillstyle=fill_style,color='#ed0345',label=label))

	x_major_locator=MultipleLocator(0.2) #把x轴的刻度间隔设置为0.2，并存在变量里
	ax1.xaxis.set_major_locator(x_major_locator)
	#ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
	#ax1.yaxis.set_major_formatter(ymajorFormatter)
	regr=LinearRegression()
	regr.fit(x_fit.reshape(-1,1),y_fit)
	line_1=ax1.plot(x_fit,regr.predict(x_fit.reshape(-1,1)),color='#01545a',label=r'E$_{a1}$')

	regr=LinearRegression()
	regr.fit(x_fit.reshape(-1,1),z_fit)
	line_2=ax1.plot(x_fit,regr.predict(x_fit.reshape(-1,1)),color='#ed0345',label=r'$E_{a2}$')

	plt.text(1.4,0.45,r"$R^2=0.60$",color='#01545a',fontsize=16)
	plt.text(1.15,0.6,r"$R^2=0.83$",color='#ed0345',fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.xlabel(r'$E_{v}$ / eV',fontsize=18)
	plt.ylabel(r'$E_{a}$ / eV',fontsize=18)
	labels=[r'clean  surface',r'hydro surface',r'$E_{a1}$',r'$E_{a2}$']
	#first_legend=plt.legend([(points_1[i][0],points_2[i][0]) for i in range(4)],labels,handler_map={tuple: HandlerTuple(ndivide=None)},fontsize=14,ncol=2)
	first_legend=plt.legend([(points_1[i][0],points_2[i][0]) for i in range(2)]+[line_1[0],line_2[0]],labels,handler_map={tuple: HandlerTuple(ndivide=None)},fontsize=14,ncol=2)
	#plt.gca().add_artist(first_legend)
	#plt.legend(handles=[line_1[0],line_2[0]],loc='lower right',fontsize=14,ncol=2)

	#ax2=ax1.twinx()
	#fig.legend(loc='center',bbox_to_anchor=(1,1),bbox_transform=ax1.transAxes)

main()

