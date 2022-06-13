#!/usr/bin/env python

import numpy as np
from functools import wraps
from matplotlib import pyplot as plt

def plot_wrap(func):
	"""图像类的装饰器，增加字体，字号功能"""
	@wraps(func)
	def wrapper(*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.markersize']=3
		func(*args,**kargs)
		bwith=3
		ax=plt.gca()
		ax.spines['bottom'].set_linewidth(bwith) # 设置边框宽度
		ax.spines['left'].set_linewidth(bwith)
		ax.spines['top'].set_linewidth(bwith)
		ax.spines['right'].set_linewidth(bwith)
		plt.tick_params(axis='y',which='both')
		plt.tick_params(width=2,length=4)
		#plt.xticks([1,3,5,7,9,11,13,15,17],[r'$IS$',r'$CH_3OH*$','TS1',r'$CH_3O*+H*$','TS2',r'$CH_2O*+2H*$',r'$CH_2O(t)*+2H*$','TS3'],fontsize=22,rotation=15)
		plt.xticks([])
		plt.yticks(fontsize=22)
		plt.xlim((0.5,15.5))
		plt.ylim((-2.6,0.9))
		#plt.xlabel(self.xlabel,fontsize=24)
		#plt.ylabel(self.ylabel,fontsize=24)
		#plt.legend(loc='best')
	return wrapper

def read(filename):
	with open(filename) as f:
		data=f.readlines()

	LATT=np.array([[float(item) for item in line.split()] for line in data[2:5]])
	NION=np.sum(np.array([int(item) for item in data[6].split()]))
	POS_d=np.array([[float(item) for item in line.split()[:3]] for line in data[9:9+NION]])
	return LATT,POS_d

def dist(LATT,POS1,POS2):
	diff=(POS1-POS2)
	diff=np.where(diff<=-0.5,diff+1,diff)
	diff=np.where(diff>=0.5,diff-1,diff)
	diff_c=np.dot(diff,LATT)
	return np.sqrt(np.sum(diff_c**2,axis=1))

@plot_wrap
def main():
	LATT,POS_IS=read("IS_sort")
	_,POS_FS=read("FS_sort")
	index1=list(range(10,25+1,1))
	index2=list(range(122,137+1,1))
	index3=list(range(90,105+1,1))
	index4=list(range(138,153+1,1))
	index=np.array(index1+index2+index3+index4)-10
	DIST=dist(LATT,POS_IS,POS_FS)
	print(np.average(DIST[index]))
	plt.plot(DIST[index],'o-')
	plt.savefig("figure.png",dpi=300)

main()