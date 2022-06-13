#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by 周慧，2019-3-9
#modified at 2019/03/20
#modified at 2019/03/24 一次处理多个cell文件
#modified at 2019/03/26-2019/03/27 写INCAR文件
import math
import os
import re
import subprocess
from collections import Counter
from functools import reduce
from operator import add
from pandas import DataFrame

from INCAR_module.run import Incar
from INCAR_module.logger import *

class Input:
	"""根据.cell文件创建INCAR、KPOINTS、POSCAR、POTCAR和vasp.script"""
	def __init__(self,limit,system,file,pot='PAW_PBE'): #['PAW_PBE','PAW_LDA','PAW_PW91','USPP_LDA','USPP_PW91']
		self.limit=limit #固定分子坐标
		self.system=system
		self.file=file
		self.vector,self.DATA_cor=Input.__cell_read(self)
		self.pot=pot
		self.dir=self.file.split('.')[0]
		if not os.path.exists(self.dir):
			os.system('mkdir {}'.format(self.dir))

	@staticmethod
	def __cell_read(self):
		"""读取.cell文件，获取基矢和原子坐标信息，返回vector列表和DATA_cor二维表（携带TF信息）"""
		with open(self.file) as f:
			data=f.readlines()
			vector=data[1:4]
		for index,line in enumerate(data):
			if re.search('\%BLOCK POSITIONS_FRAC',line):
				start=index+1
			if re.search('\%ENDBLOCK POSITIONS_FRAC',line):
				end=index
		coordinate=[]
		for item in data[start:end]:
			result=item.rstrip().split()
			result.append('T')
			coordinate.append(result)
		DATA_cor=DataFrame(coordinate,columns=['symbol','cor_x','cor_y','cor_z','info'])
		Z_value=[float(i) for i in DATA_cor['cor_z'].values]
		if self.limit!=0:
			for index,value in enumerate(Z_value):
				if value<=self.limit:
					DATA_cor.loc[index]['info']='F' #固定原子
		print("POSCAR共有{}个原子，其中固定原子有{}个。".format(len(DATA_cor.index),len(DATA_cor[DATA_cor['info']=='F'].index)))
		return vector,DATA_cor

	def write_POSCAR(self):
		"""输出POSCAR文件"""
		os.system('rm {}/POSCAR'.format(self.dir))
		elements=Counter(self.DATA_cor['symbol'].values)
		element=[key for key in elements.keys()]
		setattr(self,'element',element)
		with open('{}/POSCAR'.format(self.dir),'w')as f:
			f.write(self.system+'\n')
			f.write('1\n')
			for line in self.vector:
				f.write(line)
			for key in elements.keys():
				f.write(key+' ')
			f.write('\n')
			for value in elements.values():
				f.write(str(value)+' ')
			f.write('\nSelective Dynamics\n')
			f.write('Direct\n')
			for i in range(0,len(self.DATA_cor.index)):
				f.write('{0:>20s}  {1:>20s}  {2:>20s}  '.format(self.DATA_cor.loc[i]['cor_x'],self.DATA_cor.loc[i]['cor_y'],self.DATA_cor.loc[i]['cor_z'])+(self.DATA_cor.loc[i]['info']+'  ')*3+'\n')
		os.system("sed -n '6,7p' {}/POSCAR".format(self.dir)) #输出原子信息

	def write_POTCAR(self):
		"""输出POTCAR文件"""
		os.system('rm {}/POTCAR'.format(self.dir))
		for element in self.element:
			filepath=os.path.join(os.getcwd(),'POT/{}/{}/POTCAR'.format(self.pot,element))
			os.system('cat {0} >>{1}/POTCAR'.format(filepath,self.dir))
		print("POTCAR:所用赝势为{}".format(self.pot.split('_')[1]))

	@staticmethod
	def __vector_list(self):
		for elem in self.vector:
			yield [float(item) for item in elem.rstrip().split()]

	@staticmethod
	def __Kpoints_info(self):
		for vector in Input.__vector_list(self):
			vector_pow=[elem**2 for elem in vector]
			yield math.ceil(20.0/math.sqrt(reduce(add,vector_pow)))

	def write_KPOINTS(self,gamma=False):
		"""输出KPOINTS文件，2019/03/19增加"""
		setattr(self,'gamma',gamma)
		os.system('rm {}/KPOINTS'.format(self.dir))
		vectors=[]
		if gamma==False:
			a,b,c=tuple(Input.__Kpoints_info(self))
		else:
			a,b,c=1,1,1
		print("Kpoints:{},{},{}".format(a,b,c))
		header="Atomatically generated\n0\nG\n{}  {}  {}\n0 0 0\n".format(str(a),str(b),str(c))
		with open('{}/KPOINTS'.format(self.dir),'w') as f:
			f.write(header)

	def write_vasp_script(self,nodes=20):
		"""输出vasp.scripts文件，控制核数"""
		setattr(self,'nodes',nodes)
		os.system('cp vasp.script {}/'.format(self.dir))
		os.system("sed -i '' '6s/ppn=20/ppn={}/' {}/vasp.script".format(str(nodes),self.dir))

	def write_INCAR(self,U={},*kargs):
		incar=Incar(mode='opt',SYSTEM=self.system,pot=self.pot,nodes=self.nodes)
		incar.set_(LREAL='Auto') if self.gamma==False else incar.set_(LREAL='.False.')
		if len(U)!=0:
			incar.U_plus(U,self.element)
		incar.set_(*kargs)
		incar.create(self.dir)

def main():
	files=[name for name in os.listdir('.') if name.endswith('.cell')]
	for file in files:
		input_=Input(0.25,'CeO2',file,pot='PAW_PW91')
		input_.write_POSCAR()
		input_.write_POTCAR()
		input_.write_KPOINTS(gamma=False)
		input_.write_vasp_script(nodes=20)
		input_.write_INCAR(U={'Ce':['f',5]})
		logger.info('Done')
		print('')

if __name__ == '__main__':
	print('')
	main()
