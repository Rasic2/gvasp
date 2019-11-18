#!/usr/bin/env python
# -*- coding:utf-8 -*-
#modified by 周慧，2019-3-19
#modified at 2019/4/11 增加绘制多原子求和DOS
#modified at 2019/4/14 增加f电子绘制
# <--Version:1.3.0-->

import os
import re
import math
from collections import defaultdict
from pandas import DataFrame
from matplotlib import pyplot as plt
from functools import wraps

def doscar_parase():
	atom_list=[]
	Total_up=[]
	Total_down=[]
	columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down','f1_up','f1_down','f2_up','f2_down','f3_up','f3_down','f4_up','f4_down','f5_up','f5_down','f6_up','f6_down','f7_up','f7_down']
	orbitals=['s','p','d','f']
	with open('DOSCAR')as f:
		energy_list=[]
		pattern_1='^\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'(\d*?)\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'\n$'
		pattern_2='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*4+'\n$' #匹配Total_DOS
		pattern_3='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*32+'\n$' #匹配带f轨道的PDOS
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
			if not re.search(pattern_3,line):
				pattern_3='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*18+'\n$' #匹配最高d轨道的PDOS
			if re.search(pattern_3,line):
				count+=1
				tuple_=re.findall(pattern_3,line)[0]
				var=[float(item)*(-1)**index for index,item in enumerate(tuple_[1:])] #列表推导式代替for循环
				DATA.append(var)
				if count==NEDOS:
					columns=columns[:len(var)]
					orbitals=orbitals[1:int(math.sqrt(len(var)/2))]
					DATA=DataFrame(DATA,index=energy_list,columns=columns)
					DATA['up']=0.0;DATA['down']=0.0
					for orbital in orbitals:
						DATA[orbital+'_up']=0.0;DATA[orbital+'_down']=0.0
						orbital_p_up=[item for item in DATA.columns.values if item.startswith(orbital) and item.startswith('up')]
						orbital_p_down=[item for item in DATA.columns.values if item.startswith(orbital) and item.startswith('down')]
						for item in orbital_p_up:
							DATA['{}_up'.format(orbital)]+=DATA[item]
						for item in orbital_p_down:
							DATA['{}_down'.format(orbital)]+=DATA[item]
						DATA['up']+=DATA['{}_up'.format(orbital)]
						DATA['down']+=DATA['{}_down'.format(orbital)]
					atom_list.append(DATA)
					"""
					try:
						DATA=DataFrame(DATA,index=energy_list,columns=columns)
						DATA['p_up']=DATA['py_up']+DATA['pz_up']+DATA['px_up']
						DATA['p_down']=DATA['py_down']+DATA['pz_down']+DATA['px_down']
						DATA['d_up']=DATA['dxy_up']+DATA['dyz_up']+DATA['dz2_up']+DATA['dxz_up']+DATA['dx2_up']
						DATA['d_down']=DATA['dxy_down']+DATA['dyz_down']+DATA['dz2_down']+DATA['dxz_down']+DATA['dx2_down']
						DATA['f_up']=DATA['f1_up']+DATA['f2_up']+DATA['f3_up']+DATA['f4_up']+DATA['f5_up']+DATA['f6_up']+DATA['f7_up']
						DATA['f_down']=DATA['f1_down']+DATA['f2_down']+DATA['f3_down']+DATA['f4_down']+DATA['f5_down']+DATA['f6_down']+DATA['f7_down']
						DATA['up']=DATA['s_up']+DATA['p_up']+DATA['d_up']+DATA['f_up']
						DATA['down']=DATA['s_down']+DATA['p_down']+DATA['d_down']+DATA['f_down']
					except AssertionError:
						DATA=DataFrame(DATA,index=energy_list,columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down'])
						DATA['p_up']=DATA['py_up']+DATA['pz_up']+DATA['px_up']
						DATA['p_down']=DATA['py_down']+DATA['pz_down']+DATA['px_down']
						DATA['d_up']=DATA['dxy_up']+DATA['dyz_up']+DATA['dz2_up']+DATA['dxz_up']+DATA['dx2_up']
						DATA['d_down']=DATA['dxy_down']+DATA['dyz_down']+DATA['dz2_down']+DATA['dxz_down']+DATA['dx2_down']
						DATA['up']=DATA['s_up']+DATA['p_up']+DATA['d_up']
						DATA['down']=DATA['s_down']+DATA['p_down']+DATA['d_down']
					finally:
					"""
	Total_Dos=DataFrame(index=energy_list,columns=['tot_up','tot_down'])
	Total_Dos['tot_up']=Total_up
	Total_Dos['tot_down']=Total_down #total_dos
	atom_list.insert(0,energy_list) #pdos
	return Total_Dos,atom_list #[0]代表DOS能量范围列表，[1],[2],[3]...代表第$个原子的态密度

def contcar_require():
	"""读取CONTCAR，获得元素列表 e.g. ['','Be','Be','C']"""
	elem_name,elem_count=os.popen("sed -n '6p' CONTCAR"),os.popen("sed -n '7p' CONTCAR")
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
		func(self,*args,**kargs)
		plt.xlim((self.atom_list[0][0],self.atom_list[0][-1])) if self.xlim==None else plt.xlim(self.xlim)
		plt.xticks(fontsize=14) #坐标轴刻度
		plt.yticks(fontsize=14)
		plt.xlabel('Energy/eV',fontsize=16) #坐标轴标签
		plt.ylabel('Density of states',fontsize=16)
	return wrapper

class DOS():
	def __init__(self,xlim=None,show=True,**atoms):
		"""
		-->不指定参数，画TOT_DOS
		-->原子列表，画原子Plus_DOS
		   --> 指定原子列表，同时指定轨道，画该轨道下plus_dos
		-->单个原子，不指定轨道，atom_tot
		-->单个原子，指定轨道，PDOS
		"""
		self.total_dos,self.atom_list=doscar_parase()
		self.element=contcar_require()
		self.atom=None
		self.orbital=None
		self.xlim=xlim
		self.atoms=atoms
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
		elif self.atom and self.orbital is None:
			self.__plot_atom_tot()
		else:
			self.__plot_orbital()

	def __plot_tot(self):
		"""给出全部原子的total_up、total_down图，modified at 2019/03/19"""
		for column in self.total_dos.columns.values:
			plt.plot(self.total_dos.index.values,list(self.total_dos[column].values),linewidth=2,label=column)
		plt.legend(loc='best')

	def __plot_plus_tot(self):
		"""给出多原子求和的DOS，modified at 2019/4/12"""
		plus_tot=defaultdict(list)
		plus_tot=DataFrame(plus_tot,index=self.atom_list[0],columns=['up','down','s_up','s_down','p_up','p_down','d_up','d_down','f_up','f_down'])
		plus_tot.iloc[:,:]=0.0
		for atom in self.atoms['atom']:
			for column in plus_tot.columns.values:
				try:
					plus_tot[column]+=self.atom_list[atom][column]
				except KeyError:
					plus_tot[column]=0
		if self.orbital==None:
			plt.plot(plus_tot.index.values,plus_tot['up'].values,linewidth=2)
			plt.plot(plus_tot.index.values,plus_tot['down'].values,linewidth=2)
		else:
			for orbital in self.orbital:
				plt.plot(plus_tot.index.values,plus_tot['{}_up'.format(orbital)],linewidth=2)
				plt.plot(plus_tot.index.values,plus_tot['{}_down'.format(orbital)],linewidth=2)

	def __plot_atom_tot(self):
		"""给出单个原子的up、down图"""
		plt.plot(self.atom_list[0],list(self.atom_list[self.atom]['up'].values),linewidth=2,label=self.element[self.atom]+'_up')
		plt.plot(self.atom_list[0],list(self.atom_list[self.atom]['down'].values),linewidth=2,label=self.element[self.atom]+'_down')
		plt.legend(loc='best')

	def __plot_orbital(self):
		"""绘制单个原子的多种orbital"""
		try:
			for orbital in self.orbital:
				plt.plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_up'].values),linewidth=2,label=self.element[self.atom]+'_'+orbital+'_up') #modified at 2019/03/19 添加显示元素功能
				plt.plot(self.atom_list[0],list(self.atom_list[self.atom][orbital+'_down'].values),linewidth=2,label=self.element[self.atom]+'_'+orbital+'_down')
		except KeyError:
			print("Warning:Don't plot this non-exist orbital!")
			setattr(self,'show',False)
		else:
			plt.legend(loc='best')

fig=plt.figure(figsize=(9,5))
#DOS()
DOS(atom=1,orbital=['s'])
#DOS(atom=list(range(30,44,1)),orbital=['s'])
#DOS(atom=3,orbital=['s','p'])
#DOS(atom=3)
#plt.savefig('total.png',dpi=300,bbox_inches='tight')
