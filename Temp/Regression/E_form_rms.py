#!/usr/bin/env python

import numpy as np
from functools import wraps
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
from pandas import DataFrame

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

@plot_wrapper
def main():
	x=np.array([0.18,0.54,0.65,0.86])
	y1=np.array([1.535,1.583,1.606,1.625])
	y2=np.array([3.63,3.55,3.17,2.7])
	df=DataFrame([x,y1,y2],columns=['TSA','TSB','TSC','TSD'],index=['x','y1','y2'])

	fig=plt.figure(figsize=(5.5,5.5))
	ax1=fig.add_subplot(111)
	markers=['o','v','^','D']
	#ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
	#ax1.yaxis.set_major_formatter(ymajorFormatter)
	regr=LinearRegression()

	regr.fit(x.reshape(-1,1),y1)
	#ax1.plot(x,y1,'o',color="#01545a")
	ax1.plot(x,regr.predict(x.reshape(-1,1)),color="#01545a",label="Length")
	plt.xticks(fontsize=13)
	plt.yticks(fontsize=13)
	plt.xlabel(r'$E_a/(eV)$',fontsize=16)
	plt.ylabel(r'O-O bonding length(Å)',fontsize=16)
	plt.ylim((1.52,1.65))

	ax2=ax1.twinx()
	regr.fit(x.reshape(-1,1),y2)
	#ax2.plot(x,y2,'D',color='#ed0345')
	ax2.plot(x,regr.predict(x.reshape(-1,1)),color="#ed0345",label=r"ΔH")
	plt.yticks(fontsize=13)
	plt.ylabel(r'ΔH/(eV)',fontsize=16)
	for column,marker in zip(df.columns.values,markers):
		ax1.plot(df[column][0],df[column][1],marker,color='#01545a')
		ax2.plot(df[column][0],df[column][2],marker,color='#ed0345')
	fig.legend(loc='best',bbox_to_anchor=(1,1),bbox_transform=ax1.transAxes)

	#plt.text(1.614,0.84,"TSA",fontsize=14)
	#plt.text(1.532,0.305,"TSB",fontsize=14)
	#plt.text(1.608,0.64,"TSC",fontsize=14)
	#plt.text(1.585,0.50,"TSD",fontsize=14)
	#SS_res=np.sum((regr.predict(x.reshape(-1,1))-y)**2)
	#SS_tot=np.sum(y**2)
	#R=(SS_tot-SS_res)/(SS_tot) #(总平方和-残差平方和)/总平方和
	#print(R)

main()

