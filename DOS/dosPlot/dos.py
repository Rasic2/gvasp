#!/usr/bin/env python

import os
import math
import time
import glob
import profile,pstats
from concurrent import futures
from collections import defaultdict
import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy import interpolate
from scipy.integrate import simps
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from functools import wraps

from c_doscar_load import doscar_load #.so文件

pd.set_option('display.max_columns', None) #显示所有列
pd.set_option('display.max_rows', None) #显示所有行

def datatype_convert(energy_list,Total_up,Total_down,atom_list,length):
	columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down','f1_up','f1_down','f2_up','f2_down','f3_up','f3_down','f4_up','f4_down','f5_up','f5_down','f6_up','f6_down','f7_up','f7_down']
	orbitals=['s','p','d','f']
	atom_data=[]
	Total_Dos=DataFrame(index=energy_list,columns=['tot_up','tot_down'], dtype='object')
	Total_Dos['tot_up']=Total_up
	Total_Dos['tot_down']=Total_down
	atom_data.append(energy_list)
	columns=columns[:length]
	orbitals_fin=orbitals[1:int(math.sqrt(length/2))]
	for data in atom_list:
		DATA=DataFrame(data,index=energy_list,columns=columns)
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
		atom_data.append(DATA)
	return Total_Dos,atom_data

def doscar_parse(DOSCAR):
	energy_list,Total_up,Total_down,atom_list,length=doscar_load(DOSCAR)
	Total_Dos,atom_data=datatype_convert(energy_list,Total_up,Total_down,atom_list,length)
	return Total_Dos,atom_data

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
		plt.rc('font',family='Arial') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		plt.rcParams['lines.linewidth']=2 #配置线条宽度
		plt.rcParams['lines.color']=self.color #配置线条颜色
		func(self,*args,**kargs)
		plt.xlim((self.atom_list[0][0],self.atom_list[0][-1])) if self.xlim==None else plt.xlim(self.xlim)
		plt.ylim([-15,15])
		plt.xticks(fontsize=26) #if self.xlim==None else plt.xticks(np.linspace(self.xlim[0],self.xlim[1],int((self.xlim[1]-self.xlim[0])/0.4)),fontsize=14)#坐标轴刻度
		plt.yticks(fontsize=26)
		plt.xlabel('Energy (eV)',fontsize=28) #坐标轴标签
		plt.ylabel('Density of States (a.u.)',fontsize=28)
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
		self.total_dos,self.atom_list=doscar_parse(self.DOSCAR)
		self.element=contcar_require(self.CONTCAR)

	def plot(self,xlim=None,show=False,color='',method='fill',**kargs):
		"""实例化一个DOS对象
		1、可以指定x坐标范围
		2、指定是否将DOS分别绘制
		"""
		DOS(self.total_dos,self.atom_list,self.element,xlim=xlim,show=show,color=color,method=method,**kargs)

	def center(self,atoms=None,orbitals=None,xlim=None):
		"""计算DOS 特定原子轨道的center值"""

		old_atoms=atoms
		if isinstance(old_atoms, str): #modified at 2019/04/20 实现'a-b'代替列表求plot_dos
			if '-' in old_atoms:
				pre_atom=[int(item) for item in old_atoms.split('-')]
				atoms=list(range(pre_atom[0],pre_atom[1]+1,1))
			else:
				atoms=[index for index,element in enumerate(self.element) if old_atoms==element]
				print(atoms)
				# exit()

		y=0
		rang=(self.total_dos.index.values<xlim[1])&(self.total_dos.index.values>xlim[0])
		if atoms is None:
			y+=self.total_dos.loc[rang,'tot_up']
			y-=self.total_dos.loc[rang,'tot_down']
		elif orbitals is not None:
			for atom in atoms:
				for orbital in orbitals:
					y+=self.atom_list[atom].loc[rang,'{}_up'.format(orbital)]
					y-=self.atom_list[atom].loc[rang,'{}_down'.format(orbital)]
		else:
			for atom in atoms:
				y+=self.atom_list[atom].loc[rang,'up']
				y-=self.atom_list[atom].loc[rang,'down']
		e_count=simps(y.values,y.index.values) #辛普森积分方法，计算电子数
		dos=simps([a*b for a,b in zip(y.values,y.index.values)],y.index.values)
		print("电子数为: {0:.4f} center值为: {1:.4f}".format(e_count,dos/e_count))

def interpolated_plot(x,y,number=1,label='',color='',method='',avgflag=False):
	"""数据拟合函数，返回拟合后的x和y""" #modified at 2019/05/25 DOS数据三次插值拟合
	# method---控制绘图填充方法(fill/line) modified at 2019/06/25
	count=len(x)
	#print(count)
	x_arr=np.array(x)
	y_arr=np.array(y)
	x_new=np.linspace(x_arr.min(),x_arr.max(),count*100)
	#f=interpolate.PchipInterpolator(x_arr,y_arr)
	f=interpolate.interp1d(x_arr,y_arr,kind='cubic')
	y_new=f(x_new)

	if not avgflag:
		number = 1

	if method=='fill':
		plt.fill(x_new,y_new/number,label=label,color=color)
	elif method=='line':
		plt.plot(x_new,y_new/number,label=label,color=color)
	elif method=='dash line':
		plt.plot(x_new,y_new/number,'--',label=label,color=color)
	elif method=='output':
		file_prefix=time.strftime("%H-%M-%S",time.localtime())
		np.savetxt("datafile_x_{}".format(file_prefix),x_new)
		np.savetxt("datafile_y_{}".format(file_prefix),y_new)
		#print("Unsupported method!!! Using default setting!")
		#plt.plot(x_new,y_new,label=label,color=color)

class DOS():
	def __init__(self,total_dos,atom_list,element,color,xlim=None,show=False,method=None,avgflag=False,**kargs):
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
		self.atoms=None
		self.orbitals=None
		self.xlim=xlim
		self.kargs=kargs
		self.color=color
		self.method=method
		self.avgflag=avgflag # modified at 2022/05/07 是否计算平均DOS选项（按原子数）
		for key,value in self.kargs.items():
			setattr(self,key,value)
		self.show=show
		self.__plot
		if self.show==True:
			plt.show()

	@property
	@plot_wrapper
	def __plot(self):
		"""DOS画图函数"""
		if 'atoms' not in self.kargs.keys():
			self.__plot_tot()
		elif isinstance(self.kargs['atoms'],list):
			self.__plot_plus_tot()
		elif isinstance(self.kargs['atoms'],str): #modified at 2019/04/20 实现'a-b'代替列表求plot_dos
			if '-' in self.kargs['atoms']:
				pre_atom=[int(item) for item in self.kargs['atoms'].split('-')]
				setattr(self,'atoms',list(range(pre_atom[0],pre_atom[1]+1,1)))
			else:
				self.atoms=[index for index,element in enumerate(self.element) if self.kargs['atoms']==element]
				# print(self.atom)
				# exit()
			self.__plot_plus_tot()
		elif self.atoms and self.orbitals is None:
			self.__plot_atom_tot()
		else:
			self.__plot_orbital()

	def __plot_tot(self):
		"""给出全部原子的total_up、total_down图，modified at 2019/03/19"""
		for column in self.total_dos.columns.values:
			interpolated_plot(self.total_dos.index.values,list(self.total_dos[column].values),label=column,color=self.color,method=self.method)
			#plt.plot(x_new,y_new,label=column)
		plt.legend(loc='best')

	def __plot_plus_tot(self):
		"""给出多原子求和的DOS，modified at 2019/4/12"""
		columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down','f1_up','f1_down','f2_up','f2_down','f3_up','f3_down','f4_up','f4_down','f5_up','f5_down','f6_up','f6_down','f7_up','f7_down']
		plus_tot=defaultdict(list)
		plus_tot=DataFrame(plus_tot,index=self.atom_list[0],columns=['up','down','p_up','p_down','d_up','d_down','f_up','f_down']+columns, dtype='object')
		plus_tot.iloc[:,:]=0.0
		for atom in self.atoms:
			for column in plus_tot.columns.values:
				try:
					plus_tot[column]+=self.atom_list[atom][column]
				except KeyError:
					plus_tot[column]=0
		if self.orbitals==None:
			interpolated_plot(plus_tot.index.values,plus_tot['up'].values,number=len(self.atoms),color=self.color,method=self.method,avgflag=self.avgflag)
			interpolated_plot(plus_tot.index.values,plus_tot['down'].values,number=len(self.atoms),color=self.color,method=self.method,avgflag=self.avgflag)
		else:
			for orbital in self.orbitals:
				interpolated_plot(plus_tot.index.values,plus_tot['{}_up'.format(orbital)],number=len(self.atoms),color=self.color,method=self.method,avgflag=self.avgflag)
				interpolated_plot(plus_tot.index.values,plus_tot['{}_down'.format(orbital)],number=len(self.atoms),color=self.color,method=self.method,avgflag=self.avgflag)

	def __plot_atom_tot(self):
		"""给出单个原子的up、down图"""
		interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom]['up'].values),label=self.element[self.atom]+'_up',color=self.color,method=self.method)
		interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom]['down'].values),label=self.element[self.atom]+'_down',color=self.color,method=self.method)
		#plt.legend(loc='best')

	def __plot_orbital(self):
		"""绘制单个原子的多种orbital"""
		try:
			for orbital in self.orbital:
				interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_up'].values),label=self.element[self.atom]+'_'+orbital+'_up',color=self.color,method=self.method) #modified at 2019/03/19 添加显示元素功能
				interpolated_plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_down'].values),label=self.element[self.atom]+'_'+orbital+'_down',color=self.color,method=self.method)
		except KeyError:
			print("Warning:Don't plot this non-exist orbital!")
			setattr(self,'show',False)
		else:
			plt.legend(loc='best')

def main_wrapper(func):
	"""main函数封装 modified at 2019/04/25"""
	@wraps(func)
	def wrapper(*args,**kargs):
		fig=plt.figure(figsize=(10,8))
		func(*args,**kargs)
		if args[0]=='show':
			plt.show()
		elif args[0]=='save':
			plt.savefig('figure.svg',dpi=300,bbox_inches='tight',format='svg')

	return wrapper

def future(DOSCAR,CONTCAR):
	"main函数多进程并行future对象 modified at 2019/04/25"
	return PlotDOS(DOSCAR,CONTCAR)

@main_wrapper
def main(option):
	datafiles=glob.glob("datafile*")

	name='Ce10O21-3py'
	# DS=[f'DOSCAR-Ce3O7-3py-H','DOSCAR-Ce6O13-3py-H','DOSCAR-Ce10O21-3py-H']
	# CS=[f'CONTCAR-Ce3O7-3py-H','CONTCAR-Ce6O13-3py-H','CONTCAR-Ce10O21-3py-H']
	DS=[f'DOSCAR-{name}']
	CS=[f'CONTCAR-{name}']

	print("正在加载文件...")
	with futures.ProcessPoolExecutor() as executor:
		P=executor.map(future,DS,CS)
	P=list(P)
	print("文件加载完成...")

	# P[0].plot(atoms='185-232', orbitals=['d'], xlim=[-6,9], color='#123E09', method='line',avgflag=True)
	# P[0].plot(atoms='191-238', orbitals=['d'], xlim=[-6,9], color='#123E09', method='line',avgflag=True)
	P[0].plot(atoms='199-246', orbitals=['d'], xlim=[-6,9], color='#123E09', method='line',avgflag=True)
	P[0].plot(atoms='Ce', orbitals=['f'], xlim=[-6,9], color='#ed0345', method='line',avgflag=True)
	P[0].plot(atoms='1-33',xlim=[-6,9],color='#B30099', method='line') # pyridine
	# P[0].plot(atoms=[12,14], xlim=[-36,10], color='#B30099', method='line',)

	# P[0].center(atoms='Ce',xlim=[-6,0],orbitals=['f'])
	# P[0].center(atoms='Cu',xlim=[-6,0],orbitals=['d'])
	# P[0].center(atoms='C',xlim=[-6,0])
	# P[0].center(atoms='N',xlim=[-6,0])
	# P[0].center(atoms=[13,16],xlim=[-6,0]) # (13,16) (16,17), (12,14)

if __name__ == '__main__':
	main('show')
	# main('')

#profile.run('main("")','result')
#p=pstats.Stats("result")
#p.strip_dirs().sort_stats("time").print_stats()