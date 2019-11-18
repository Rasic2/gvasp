#!/usr/bin/env python
# -*- coding:utf-8 -*-
#modified by 周慧，2019-3-19
#modified at 2019/4/11 增加绘制多原子求和DOS
#modified at 2019/4/14 增加f电子绘制
#modified at 2019/4/20 简化绘制多个原子的API
#modified at 2019/4/22 性能优化,DOSCAR、CONTCAR设置只读一次
#inspired by 刘颖,modified at 2019/4/25 增加读入多个DOSCAR文件进行数据对比分析
#modified at 2019/04/26 全局修改线宽
#modified at 2019/05/25 增加DOS数据三次插值拟合,提供颜色参数
# <--Version:1.5.4-->

import os
import re
import math
from concurrent import futures
from collections import defaultdict
import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy import interpolate
from matplotlib import pyplot as plt
from functools import wraps

pd.set_option('display.max_columns', None) #显示所有列
pd.set_option('display.max_rows', None) #显示所有行

def doscar_parase(DOSCAR,max_orbital):
	"""解析DOSCAR文件"""
	atom_list=[]
	Total_up=[]
	Total_down=[]
	columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down','f1_up','f1_down','f2_up','f2_down','f3_up','f3_down','f4_up','f4_down','f5_up','f5_down','f6_up','f6_down','f7_up','f7_down']
	orbitals=['s','p','d','f']
	option={'d':18,'f':32}
	with open('{}'.format(DOSCAR))as f:
		energy_list=[]
		pattern_1='^\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'(\d*?)\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'\n$'
		pattern_2='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*4+'\n$' #匹配Total_DOS
		pattern_3='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*option[max_orbital]+'\n$' #匹配带f轨道的PDOS
		for line in f.readlines()[5:]:
			if re.search(pattern_1,line):
				NEDOS=int(re.findall(pattern_1,line)[0][2])
				E_Fermi=float(re.findall(pattern_1,line)[0][3])
				count=0
				DATA=[]
			if re.search(pattern_2,line):
				line_array=line.split()
				energy_list.append(float(line_array[0])-E_Fermi)
				Total_up.append(float(line_array[1]))
				Total_down.append(-float(line_array[2]))
			if re.search(pattern_3,line):
				count+=1
				tuple_=re.findall(pattern_3,line)[0]
				var=[float(item)*(-1)**index for index,item in enumerate(tuple_[1:])] #列表推导式代替for循环
				DATA.append(var)
				if count==NEDOS:
					columns=columns[:len(var)]
					orbitals_fin=orbitals[1:int(math.sqrt(len(var)/2))]
					DATA=DataFrame(DATA,index=energy_list,columns=columns)
					DATA['up']=0.0;DATA['down']=0.0
					for orbital in orbitals_fin:
						DATA[orbital+'_up']=0.0;DATA[orbital+'_down']=0.0
						orbital_p_up=[item for item in DATA.columns.values if item.startswith(orbital) and item.endswith('up') and item!='{}_up'.format(orbital) and item!='up']
						orbital_p_down=[item for item in DATA.columns.values if item.startswith(orbital) and item.endswith('down') and item!='{}_down'.format(orbital) and item!='down']
						for item in orbital_p_up:
							DATA['{}_up'.format(orbital)]+=DATA[item]
						for item in orbital_p_down:
							DATA['{}_down'.format(orbital)]+=DATA[item]
						DATA['up']+=DATA['{}_up'.format(orbital)]
						DATA['down']+=DATA['{}_down'.format(orbital)]
					DATA['up']+=DATA['s_up']
					DATA['down']+=DATA['s_down']
					atom_list.append(DATA)
	Total_Dos=DataFrame(index=energy_list,columns=['tot_up','tot_down'])
	Total_Dos['tot_up']=Total_up
	Total_Dos['tot_down']=Total_down #total_dos
	atom_list.insert(0,energy_list) #pdos
	return Total_Dos,atom_list #[0]代表DOS能量范围列表，[1],[2],[3]...代表第$个原子的态密度

def contcar_require(CONTCAR):
	"""读取CONTCAR，获得元素列表 e.g. ['','Be','Be','C']"""
	elem_name,elem_count=os.popen("sed -n '6p' {}".format(CONTCAR)),os.popen("sed -n '7p' {}".format(CONTCAR))
	names=elem_name.read().rstrip().split()
	counts=[int(item) for item in elem_count.read().rstrip().split()]
	result=['']
	for index,count in enumerate(counts):
		while count!=0:
			result.append(names[index])
			count-=1
	return result

def plot_wrapper(func):
	@wraps(func)
	def wrapper(self,*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=2 #配置线条宽度
		plt.rcParams['lines.color']=self.color #配置线条颜色
		func(self,*args,**kargs)
		plt.xlim((self.atom_list[0][0],self.atom_list[0][-1])) if self.xlim==None else plt.xlim(self.xlim)
		plt.xticks(fontsize=14) if self.xlim==None else plt.xticks(np.linspace(self.xlim[0],self.xlim[1],int((self.xlim[1]-self.xlim[0])/0.4)),fontsize=14)#坐标轴刻度
		plt.yticks(fontsize=14)
		plt.xlabel('Energy/eV',fontsize=16) #坐标轴标签
		plt.ylabel('Density of states',fontsize=16)
	return wrapper

class PlotDOS():
	"""API接口 modified at 2019/04/25
	__load:加载DOSCAR、CONTCAR或POSCAR数据
	plot():绘制DOS
	"""
	def __init__(self,DOSCAR,CONTCAR,max_orbital='f'):
		self.DOSCAR=DOSCAR
		self.CONTCAR=CONTCAR
		self.max_orbital=max_orbital #指定有没有f轨道需要处理，默认只处理d轨道
		self.__load()

	def __load(self):
		self.total_dos,self.atom_list=doscar_parase(self.DOSCAR,self.max_orbital)
		self.element=contcar_require(self.CONTCAR)

	def plot(self,xlim=None,show=False,color='',**atoms):
		"""实例化一个DOS对象
		1、可以指定x坐标范围
		2、指定是否将DOS分别绘制
		"""
		DOS(self.total_dos,self.atom_list,self.element,xlim=xlim,show=show,color=color,**atoms)

def interpolated_plot(x,y,label='',color=''):
	"""数据拟合函数，返回拟合后的x和y""" #modified at 2019/05/25 DOS数据三次插值拟合
	count=len(x)
	#print(count)
	x_arr=np.array(x)
	y_arr=np.array(y)
	x_new=np.linspace(x_arr.min(),x_arr.max(),count*100)
	#f=interpolate.PchipInterpolator(x_arr,y_arr)
	f=interpolate.interp1d(x_arr,y_arr,kind='cubic')
	y_new=f(x_new)
	plt.plot(x_new,y_new,label=label,color=color)

class DOS():
	def __init__(self,total_dos,atom_list,element,color,xlim=None,show=False,**atoms):
		"""
		-->不指定参数，画TOT_DOS								e.g. DOS()
		-->原子列表，画原子Plus_DOS							e.g. DOS(atom=[1,2,3])
		   --> 指定原子列表，同时指定轨道，画该轨道下plus_dos	e.g. DOS(atom=[1,3,4],orbital=['s','p'])
		   --> 简化获取连续多原子方法							e.g. DOS(atom='1-3',orbital=['s','p'])
		-->单个原子，不指定轨道，atom_tot						e.g. DOS(atom=1)
		-->单个原子，指定轨道，PDOS							e.g. DOS(atom=1,orbital=['s','p'])
		"""
		#super().__init__()
		self.total_dos=total_dos
		self.atom_list=atom_list
		self.element=element
		self.atom=None
		self.orbital=None
		self.xlim=xlim
		self.atoms=atoms
		self.color=color
		for key,value in self.atoms.items():
			setattr(self,key,value)
		self.show=show
		self.__plot
		if self.show==True:
			plt.show()

	@property
	@plot_wrapper
	def __plot(self):
		"""DOS画图函数"""
		if 'atom' not in self.atoms.keys():
			self.__plot_tot()
		elif isinstance(self.atoms['atom'],list):
			self.__plot_plus_tot()
		elif isinstance(self.atoms['atom'],str): #modified at 2019/04/20 实现'a-b'代替列表求plut_dos
			pre_atom=[int(item) for item in self.atoms['atom'].split('-')]
			setattr(self,'atom',list(range(pre_atom[0],pre_atom[1]+1,1)))
			self.__plot_plus_tot()
		elif self.atom and self.orbital is None:
			self.__plot_atom_tot()
		else:
			self.__plot_orbital()

	def __plot_tot(self):
		"""给出全部原子的total_up、total_down图，modified at 2019/03/19"""
		for column in self.total_dos.columns.values:
			interpolated_plot(self.total_dos.index.values,list(self.total_dos[column].values),label=column,color=self.color)
			#plt.plot(x_new,y_new,label=column)
		plt.legend(loc='best')

	def __plot_plus_tot(self):
		"""给出多原子求和的DOS，modified at 2019/4/12"""
		plus_tot=defaultdict(list)
		plus_tot=DataFrame(plus_tot,index=self.atom_list[0],columns=['up','down','s_up','s_down','p_up','p_down','d_up','d_down','f_up','f_down'])
		plus_tot.iloc[:,:]=0.0
		for atom in self.atom:
			for column in plus_tot.columns.values:
				try:
					plus_tot[column]+=self.atom_list[atom][column]
				except KeyError:
					plus_tot[column]=0
		if self.orbital==None:
			interpolated_plot(plus_tot.index.values,plus_tot['up'].values,color=self.color)
			interpolated_plot(plus_tot.index.values,plus_tot['down'].values,color=self.color)
		else:
			for orbital in self.orbital:
				interpolated_plot(plus_tot.index.values,plus_tot['{}_up'.format(orbital)],color=self.color)
				interpolated_plot(plus_tot.index.values,plus_tot['{}_down'.format(orbital)],color=self.color)

	def __plot_atom_tot(self):
		"""给出单个原子的up、down图"""
		interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom]['up'].values),label=self.element[self.atom]+'_up',color=self.color)
		interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom]['down'].values),label=self.element[self.atom]+'_down',color=self.color)
		#plt.legend(loc='best')

	def __plot_orbital(self):
		"""绘制单个原子的多种orbital"""
		try:
			for orbital in self.orbital:
				interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_up'].values),label=self.element[self.atom]+'_'+orbital+'_up',color=self.color) #modified at 2019/03/19 添加显示元素功能
				interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_down'].values),label=self.element[self.atom]+'_'+orbital+'_down',color=self.color)
		except KeyError:
			print("Warning:Don't plot this non-exist orbital!")
			setattr(self,'show',False)
		else:
			plt.legend(loc='best')

def main_wrapper(func):
	"""main函数封装 modified at 2019/04/25"""
	@wraps(func)
	def wrapper(*args,**kargs):
		fig=plt.figure(figsize=(9,5))
		func(*args,**kargs)
		if args[0]=='show':
			plt.show()
		elif args[0]=='save':
			plt.savefig('figure.png',dpi=300,bbox_inches='tight')
		else:
			print('Wrong Option!')
	return wrapper

def future(DOSCAR,CONTCAR):
	"main函数多进程并行future对象 modified at 2019/04/25"
	return PlotDOS(DOSCAR,CONTCAR)

@main_wrapper
def main(option):
	#e.g.
	DS=['DOSCAR']
	CS=['CONTCAR']
	print("正在加载文件...")
	with futures.ProcessPoolExecutor() as executor:
		P=executor.map(future,DS,CS)
	P=list(P)
	print("文件加载完成...")
	P[0].plot(atom=10,xlim=[-1.5,0.5],color='#3A7F99')
	P[0].plot(atom=12,xlim=[-1.5,0.5],color='#F69221')
	P[0].plot(atom=24,xlim=[-1.5,0.5],color='#ed0345')
	#P[0].plot(xlim=[-1,0])
if __name__ == '__main__':
	main('show')







