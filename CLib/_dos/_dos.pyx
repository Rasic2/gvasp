# distutils: language=c++
# cython:c_string_type=unicode, c_string_encoding=utf-8

from libc.stdlib cimport atoi,atof
from libcpp.vector cimport vector
from libcpp.string cimport string

import numpy as np

def load(list strings, int NDOS, double E_Fermi):
	cdef:
		list atom_list=[],DATA_list=[],line_array,Total_up=[],Total_down=[],energy_list=[]
		vector[double] var
		int count=0,index=0
		unicode line

	for line in strings:
		if index in range(6,6+NDOS):
			line_array=line.split()
			energy_list.append(atof(line_array[0])-E_Fermi)
			Total_up.append(atof(line_array[1]))
			Total_down.append(-atof(line_array[2]))
		if index>=(6+NDOS+1) and (index-5)%(NDOS+1)!=0:
			count+=1
			var=[atof(item)*(-1)**index for index,item in enumerate(line.split()[1:])]
			DATA_list.append(var)
			if count==NDOS:
				count=0
				atom_list.append(DATA_list)
				DATA_list=[]
		index+=1

	return energy_list, Total_up, Total_down, atom_list, len(var)
