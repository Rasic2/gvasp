#!/usr/bin/env python

import sys
import numpy as np
import os

def head_load():
	with open("CONTCAR") as f:
		file=f.readlines()
	head=file[:9]
	ele_num=[int(item) for item in file[6].split()]
	return file,head,ele_num

def loc_load(file,ele_num):
	locs=[]
	TFS=[]
	for line in file[9:9+sum(ele_num)]:
		line_list=line.split()
		loc=[float(item) for item in line_list if line_list.index(item) < 3]
		TF=line_list[3:]
		locs.append(loc)
		TFS.append(TF)
	return locs,TFS

def process(locs,ele_num):
	rows=int(sum(ele_num)/2)
	rand_num=np.random.randn(rows,3)
	rand_num_std=0.1*((rand_num-np.mean(rand_num))/(np.max(rand_num)-np.min(rand_num)))
	locs=np.array(locs)
	z_min=np.min(locs[:,2][np.argpartition(locs[:,2],-rows)[-rows:]])
	locs[np.where(locs[:,2]>=z_min)]+=rand_num_std
	return locs

def write(filename,head,locs,TFS):
	with open(filename,'w')as f:
		f.writelines(head)
		for item_loc,item_TF in zip(locs,TFS):
			for item in item_loc:
				f.write(str(item)+"\t")
			for item in item_TF:
				f.write(item+"\t")
			f.write("\n")

def main():
	file,head,ele_num=head_load()
	locs_ori,TFS=loc_load(file,ele_num)
	for i in range(1,6):
		if(os.path.exists("{}".format(i)) is not True):
			os.mkdir("{}".format(i))
		locs=process(locs_ori,ele_num)
		write("{}/POSCAR".format(i),head,locs,TFS)
		os.system("cp INCAR KPOINTS POTCAR vasp.script {}/".format(i))

if __name__ == '__main__':
	main()


