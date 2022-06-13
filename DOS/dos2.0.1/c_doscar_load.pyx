# distutils: language=c++
# cython:c_string_type=unicode, c_string_encoding=utf-8

from libc.stdlib cimport atoi,atof
from libcpp.vector cimport vector
from libcpp.string cimport string

def read_genator(unicode DOSCAR):
	with open(DOSCAR) as f:
		yield from f.readlines()

def doscar_load(unicode DOSCAR):
	cdef:
		list atom_list=[],DATA_list=[],line_array,Total_up=[],Total_down=[],energy_list=[]
		vector[double] var
		int NEDOS=1000,count=0,index=0
		double E_Fermi
		unicode line

	for line in read_genator(DOSCAR):
		if index==5:
			E_Fermi=atof(line.split()[3])
			NEDOS=atoi(line.split()[2])
		if index in range(6,6+NEDOS):
			line_array=line.split()
			energy_list.append(atof(line_array[0])-E_Fermi)
			Total_up.append(atof(line_array[1]))
			Total_down.append(-atof(line_array[2]))
		if index>=(6+NEDOS+1) and (index-5)%(NEDOS+1)!=0:
			count+=1
			var=[atof(item)*(-1)**index for index,item in enumerate(line.split()[1:])] #列表推导式代替for循环
			DATA_list.append(var)
			if count==NEDOS:
				count=0
				atom_list.append(DATA_list)
				DATA_list=[]
		index+=1

	return energy_list,Total_up,Total_down,atom_list,len(var)
