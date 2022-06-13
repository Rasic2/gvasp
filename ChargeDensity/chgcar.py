#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by 周慧，2019/03/21
import re
import numpy as np

class CHGCAR_tot():
	def __init__(self,Z_value):
		self.Z_value=Z_value
		self.NGZF,self.array=self.__load()
		self.text=self.__data_treat()
	def __load(self):
		with open('CHGCAR_tot')as f:
			data=f.readlines()
		for i,line in enumerate(data):
			if re.findall('^'+'\s+?(\d+?)'*3,line):
				index=i
				break
		NGXF,NGYF,NGZF=[int(i) for i in data[index].split()]
		raw_data=[float(item) for line in data[index+1:] for item in line.split()]
		raw_data=np.array(raw_data)
		array=raw_data.reshape((40,40,200),order='F')
		return NGZF,array
	def __data_treat(self):
		z_coord=int((self.NGZF-1)*self.Z_value)
		return self.array[0,0,z_coord]

chgcar=CHGCAR_tot(0.5)
print(chgcar.NGZF)
print(chgcar.array.max())
print(chgcar.text)

