#!/usr/bin/env python

import sys
import numpy as np

NCl=int(sys.argv[1])
STEPS=int(sys.argv[2])
with open("temp_input_2") as f:
	data=f.readlines()
LINES=len(data)
Pt_list=[]
dis_list=[]
for i in range(LINES):
	if((i+1)%(LINES/STEPS)==0):
		Pt_list.append([float(i) for i in data[i].split()])
Pt_arr=np.array(Pt_list)

for i in range(NCl):
	Cl_list=[]
	for j in range(len(data)):
		if((j+1)%(LINES/STEPS)==(i+1)):
			Cl_list.append([float(j) for j in data[j].split()])
	Cl_arr=np.array(Cl_list)
	dis_arr=np.sqrt(np.sum((Pt_arr-Cl_arr)**2,axis=1))
	np.savetxt("temp_dis{}".format(i),dis_arr)	

