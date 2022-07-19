#!/usr/bin/env python

import numpy as np
from functools import wraps
from collections import Counter
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
from pandas import DataFrame
from scipy import interpolate
#import statsmodels.api as sm
#import rpy2.robjects as robjects
#from rpy2.robjects import FloatVector
#from rpy2.robjects.packages import importr

def plot_wrapper(func):
	@wraps(func)
	def wrapper(*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=3 #配置线条宽度
		plt.rcParams['lines.markersize']=9 #配置线条宽度
		func(*args,**kargs)
		plt.show()
		#plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')
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
	labels=[r'$O^A$',r'$O^B$',r'$O^C$',r'$O^D$']
	x=np.array([-1.61,-1.90,-2.25,-2.32]) #焓变
	y=np.array([0.7,0.58,0.18,0.25]) #能垒
	#y2=np.array([0.1435,0.131,0.119,0.1025]) #相近O原子距离
	#y3=np.array([0.06,0.28,0.49,0.74]) #吸附能差
	#r_ols(x,y)
	#sm_ols(y3,y1)
	#df=DataFrame([x,y1,y2,y3],columns=['TSA','TSB','TSC','TSD'],index=['x','y1','y2','y3'])

	fig=plt.figure(figsize=(8,7))
	#plt.subplots_adjust(wspace=0.5)
	ax1=fig.add_subplot(111)
	for x_,y_,color,label in zip(x,y,colors,labels):
		ax1.plot(x_,y_,'o',color=color,label=label)
	#markers=['o','v','^','D']
	x_major_locator=MultipleLocator(0.4) #把y轴的刻度间隔设置为10，并存在变量里
	ax1.xaxis.set_major_locator(x_major_locator)
	#ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
	#ax1.yaxis.set_major_formatter(ymajorFormatter)
	regr=LinearRegression()

	regr.fit(x.reshape(-1,1),y)
	#ax1.plot(x,y1,'o',color="#01545a")
	ax1.plot(x,regr.predict(x.reshape(-1,1)),color='#710162')
	plt.text(-1.6,0.4,r"$y=0.74x+1.92$",color='#000000',fontsize=16)
	plt.text(-1.55,0.37,r"$R^2=0.94$",color='#000000',fontsize=16)
	plt.xticks(fontsize=24)
	plt.yticks(fontsize=24)
	plt.ylabel(r'$E_{a1}/(eV)$',fontsize=26)
	plt.xlabel(r'∆H/(eV)',fontsize=26)
	plt.legend(loc='best',fontsize=18)
	#plt.xlim(-0.7,-2.4)
	#plt.ylim((0.11,0.89))

	"""
	ax2=ax1.twinx()
	#ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
	#ax2.yaxis.set_major_formatter(ymajorFormatter)
	#interpolated_plot(x,y2,label='distance',color='#ed0345')
	#plt.plot(x,y2,'o',color='#ed0345')
	plt.plot(x,[0.164,0.1315,0.116,0.103],color='#ed0345')
	plt.text(1.56,0.154,r"$y=-0.67x+1.20$",color='#ed0345',fontsize=14)
	plt.text(1.565,0.15,r"$R^2=0.98$",color='#ed0345',fontsize=14)
	#regr.fit(x.reshape(-1,1),y2)
	#ax2.plot(x,regr.predict(x.reshape(-1,1)),color='#ed0345',label='r')
	plt.yticks(fontsize=13)
	plt.ylabel(r'r',fontsize=16)
	#plt.ylim((2.6,3.19))

	ax3=fig.add_subplot(122)
	regr.fit(y3.reshape(-1,1),y1)
	ax3.plot(y3,regr.predict(y3.reshape(-1,1)),color='#710162')
	plt.text(0.3,0.48,r"$y=0.82x+0.26$",color='#710162',fontsize=14)
	plt.text(0.35,0.43,r"$R^2=0.99$",color='#710162',fontsize=14)
	plt.xticks(fontsize=13)
	plt.yticks(fontsize=13)
	plt.ylim(0.9,0.25)
	plt.xlabel(r"$ΔE_{ads}/(eV)$",fontsize=16)
	plt.ylabel(r'$E_a/(eV)$',fontsize=16)

	for column,marker in zip(df.columns.values,markers):
		ax1.plot(df[column][0],df[column][1],marker,color='#01545a')
		ax2.plot(df[column][0],df[column][2],marker,color='#ed0345')
		#ax3.plot(df[column][3],df[column][1],marker,color='#710162')

	#fig.legend(loc='center',bbox_to_anchor=(1,1),bbox_transform=ax1.transAxes)
	"""

main()

