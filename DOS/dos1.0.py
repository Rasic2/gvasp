#!/usr/bin/env python
# -*- coding:utf-8 -*-
#modified by 周慧，2019-3-19
#modified at 2019/4/11 增加绘制多原子求和DOS

import os
import re
import math
from collections import defaultdict
from pandas import DataFrame
from matplotlib import pyplot as plt
from functools import wraps

def doscar_require():
	atom_list=[]
	Total_up=[]
	Total_down=[]
	with open('DOSCAR')as f:
		energy_list=[]
		for line in f.readlines()[5:]:
			pattern_1='^\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'(\d*?)\s*?'+'([+-]?\d*?\.\d*?)\s*?'*2+'\n$'
			pattern_2='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*4+'\n$'
			pattern_3='^\s*?([+-]?\d*?\.\d*?)\s*?'+'(\d*?\.\d*?E[+-]?\d*?)\s*?'*18+'\n$'
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
				#energy_list.append(float(tuple_[0])-E_Fermi)
				"""
				for index,item in enumerate(tuple_[1:]):
					var.append(float(item)*(-1)**index)
				"""
				var=[float(item)*(-1)**index for index,item in enumerate(tuple_[1:])] #列表推导式代替for循环
				DATA.append(var)
				if count==NEDOS:
					DATA=DataFrame(DATA,index=energy_list,columns=['s_up','s_down','py_up','py_down','pz_up','pz_down','px_up','px_down','dxy_up','dxy_down','dyz_up','dyz_down','dz2_up','dz2_down','dxz_up','dxz_down','dx2_up','dx2_down'])
					DATA['p_up']=DATA['py_up']+DATA['pz_up']+DATA['px_up']
					DATA['p_down']=DATA['py_down']+DATA['pz_down']+DATA['px_down']
					DATA['d_up']=DATA['dxy_up']+DATA['dyz_up']+DATA['dz2_up']+DATA['dxz_up']+DATA['dx2_up']
					DATA['d_down']=DATA['dxy_down']+DATA['dyz_down']+DATA['dz2_down']+DATA['dxz_down']+DATA['dx2_down']
					DATA['up']=DATA['s_up']+DATA['p_up']+DATA['d_up']
					DATA['down']=DATA['s_down']+DATA['p_down']+DATA['d_down']
					atom_list.append(DATA)
	Total_Dos=DataFrame(index=energy_list,columns=['tot_up','tot_down'])
	Total_Dos['tot_up']=Total_up
	Total_Dos['tot_down']=Total_down #total_dos
	atom_list.insert(0,energy_list) #pdos
	return Total_Dos,atom_list #[0]代表DOS能量范围列表，[1],[2],[3]...代表第$个原子的态密度

def contcar_require():
	"""
	读取CONTCAR，获得元素列表 e.g. ['','Be','Be','C']
	"""
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
		for plt in func(self,*args,**kargs):
			plt.title('DOS',fontsize=self.fontsize,fontfamily='Times New Roman')
			plt.xlim((self.atom_list[0][0],self.atom_list[0][-1]))
			plt.ylim((self.y_min-0.1,self.y_max+0.1)) #坐标轴范围
			plt.xticks(fontsize=self.fontsize-4,fontfamily='Times New Roman') #坐标轴刻度
			plt.yticks(fontsize=self.fontsize-4,fontfamily='Times New Roman')
			plt.xlabel('Energy/eV',fontsize=self.fontsize-2,fontfamily='Times New Roman') #坐标轴标签
			plt.ylabel('density of states',fontsize=self.fontsize-2,fontfamily='Times New Roman')
			plt.legend(loc='best')
			plt.plot([0,0],[self.y_min-0.3,self.y_max+0.3],'--',linewidth=1.5,color='#008080')
		plt.show()
	return wrapper


class Plot():
	def __init__(self,*atoms):
		"""
		传递需要描绘的原子数,i.e. 1,2,3
		"""
		self.atoms=atoms
		self.total_dos,self.atom_list=doscar_require()
		self.element=contcar_require()
		self.fig=plt.figure(figsize=(8,6.5))
		self.fontsize=20
		self.plot_tot=True
		self.plot_atom_tot=True
		self.y_min=0
		self.y_max=0

	@staticmethod
	def __plot_tot(self):
		"""
		给出全部原子的total_up、total_down图，modified at 2019/03/19
		"""
		for column in self.total_dos.columns.values:
			plt.plot(self.total_dos.index.values,list(self.total_dos[column].values),'-',linewidth=2,label=column)
		self.y_min=min(self.total_dos['tot_down'].values)
		self.y_max=max(self.total_dos['tot_up'].values)

		"""
		TOT=defaultdict(list)
		TOT=DataFrame(TOT,index=self.atom_list[0],columns=['up','down'])
		TOT['up']=0.0;TOT['down']=0.0
		for data in self.atom_list[1:]:
			TOT['up']+=data['up']
			TOT['down']+=data['down']
		for column in TOT.columns.values:
			plt.plot(self.atom_list[0],list(TOT[column].values),'-',linewidth=3,label='tot_'+column)
			#plt.fill(self.atom_list[0],list(TOT[column].values))
		self.y_min=min(TOT['down'].values)
		self.y_max=max(TOT['up'].values)
		"""

	@staticmethod
	def __plot_atom_tot(self,atom):
		"""
		给出单个原子的up、down图
		"""
		plt.plot(self.atom_list[0],list(self.atom_list[atom]['up'].values),'-',linewidth=2,label=self.element[atom]+'_up')
		plt.plot(self.atom_list[0],list(self.atom_list[atom]['down'].values),'-',linewidth=2,label=self.element[atom]+'_down')
		self.y_min=min(self.atom_list[atom]['down'].values)
		self.y_max=max(self.atom_list[atom]['up'].values)

	@plot_wrapper
	def plot(self,*modes,plot_atom_tot=False,plot_tot=False,subplot=False,rows=1,columns=1,fontsize=20,y_min=-1,y_max=1):
		"""
		modes控制需要描绘的模式，传递字符串列表，i.e. 's','p','d','px','py','pz','dxy','dyz','dxz','dz2','dx2'
		可以只画单个原子的total或者加上其他模式；total控制是否需要描绘总的total
		"""
		self.fontsize=fontsize
		self.plot_atom_tot=plot_atom_tot
		self.plot_tot=plot_tot
		if len(self.atoms):
			for index in range(len(self.atoms)):
				if(subplot==True):
					rows=math.ceil(math.sqrt(len(self.atoms)))
					ax=self.fig.add_subplot(rows,columns,index+1)
				else:
					ax=plt
				atom=self.atoms[index]
				for mode in modes:
					ax.plot(self.atom_list[0],list(self.atom_list[atom][mode+'_up'].values),'-',linewidth=3,label=self.element[atom]+'_'+mode+'_up') #modified at 2019/03/19 添加显示元素功能
					ax.plot(self.atom_list[0],list(self.atom_list[atom][mode+'_down'].values),'-',linewidth=3,label=self.element[atom]+'_'+mode+'_down')
					min_y=min(self.atom_list[atom][mode+'_down'].values)
					max_y=max(self.atom_list[atom][mode+'_up'].values)
					self.y_min=min_y if self.y_min>=min_y else self.y_min
					self.y_max=max_y if self.y_max<=max_y else self.y_max
				if self.plot_atom_tot==True or len(modes)==0:
					Plot.__plot_atom_tot(self,atom)
				if self.plot_tot==True:
					Plot.__plot_tot(self)
				yield plt
		else:
			Plot.__plot_tot(self)
			yield plt

p=Plot()
#print(p.element)
p.plot(subplot=False,plot_tot=False,plot_atom_tot=False)
plt.show() #加到装饰器中
