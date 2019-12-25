#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 用于CI-NEB计算中IS与FS结构调整
# created by hui_zhou@mail.ecust.edu.cn,2019/07/16
# modified at 2019/07/18 修改确认相同原子算法
# modified at 2019/07/30 修改算法，添加PBC（周期性边界条件规则）
# modified at 2019/12/25 修改算法，增加键长信息
# <--Version:0.2.4-->

import os
import sys
import json
import numpy as np
from functools import reduce
from collections import defaultdict
from collections.abc import Iterable
#import profile,pstats

def flatten(items,ignore_types=(str,bytes,dict)):
	#扁平化序列函数#
	"""
		items: 可迭代序列
	"""
	for x in items:
		if(isinstance(x,Iterable) and not isinstance(x,ignore_types)):
			yield from flatten(x)
		else:
			yield x

def load(filename):
	#加载IS、FS结构，返回结构头文件，基矢，坐标字典#
	"""
		filename: 文件名

		-->head: POSCAR头信息
		-->base：基矢向量
		-->loc_dict：坐标字典
	"""
	with open(filename) as f:
		file=f.readlines()
	head=file[:9]
	base=np.array([[float(item) for item in line.split()] for line in head[2:5]])
	loc_dict=defaultdict(list)
	ele_name,ele_num=file[5].split(),file[6].split()
	start=9
	for key,num in zip(ele_name,ele_num):
		i=1
		for line in file[start:start+int(num)]:
			loc=[float(item) if index < 3 else item for index,item in enumerate(line.split())]
			name=str(key)+str(i)
			loc_dict[key].append({name:loc})
			i+=1
			start+=1
	return head,base,loc_dict

def bond_length(atom1,atom2,base,BondDist):
	#计算两个原子的键长，如若在默认键长范围内，认为成键(TRUE);反之，不成键(FALSE)
	"""
		atom1:第一个原子的坐标信息
		atom2:第二个原子的坐标信息
		base：基矢向量
		BondDist：json文件，存储默认键长
	"""
	mix_bond=0.6
	max_bond=1.1
	atom1_element=reduce(lambda x,y : x+y,list(filter(lambda x : x.isalpha(),list(atom1.keys())[0])))
	atom2_element=reduce(lambda x,y : x+y,list(filter(lambda x : x.isalpha(),list(atom2.keys())[0])))
	atom1_pos=np.array(list(atom1.values())[0][:3])
	atom2_pos=np.array(list(atom2.values())[0][:3])
	atom2_pos=np.where((atom2_pos-atom1_pos)>0.5,atom2_pos-1,atom2_pos)
	atom2_pos=np.where((atom2_pos-atom1_pos)<-0.5,atom2_pos+1,atom2_pos)
	length=np.sqrt(np.sum(np.dot((atom2_pos-atom1_pos),base)**2))
	default_bond=BondDist[atom1_element][atom2_element]
	if(length>=mix_bond*default_bond and length<=max_bond*default_bond):
		return True
	else:
		return False

def bond_info(base,loc_dict,ignore_bond):
	#给出IS和FS结构的成键信息，调用bond_length()函数计算成键
	"""
		base：基矢向量
		loc_dict：坐标字典
		ignore_bond：IS与FS结构主要成键信息区别

		--> bond_dict:成键信息字典
	"""
	with open("BondDist.json",'r') as f:
		BondDist=json.load(f)
	atom_tot=[atom for atom in flatten(loc_dict.values())]
	bond_dict=defaultdict(list)
	for element in loc_dict.keys():
		if(element in BondDist.keys()):
			for atom1 in loc_dict[element]:
				for atom2 in atom_tot:
					atom2_element=reduce(lambda x,y : x+y,list(filter(lambda x : x.isalpha(),list(atom2.keys())[0])))
					if(atom1!=atom2 and atom2_element in BondDist[element].keys() and bond_length(atom1,atom2,base,BondDist)):
						atom1_element=reduce(lambda x,y : x+y,list(filter(lambda x : x.isalpha(),list(atom1.keys())[0])))
						bond_dict[list(atom1.keys())[0]].append(atom1_element+"-"+atom2_element)

	ignore_bond_reverse='{0}-{1}'.format(ignore_bond.split('-')[1],ignore_bond.split('-')[0])
	for key in bond_dict.keys():
		if(ignore_bond in bond_dict[key]):
			bond_dict[key].remove(ignore_bond)
		elif(ignore_bond_reverse in bond_dict[key]):
			bond_dict[key].remove(ignore_bond_reverse)
	return bond_dict

def atom_sort(IS_dict,IS_bond_dict,FS_dict,FS_bond_dict):
	#对IS、FS坐标重新排序，考虑周期性边界条件下，最小原子距离认为是同一个原子
	"""
		IS_dict:IS坐标结构字典
		IS_bond_dict：IS成键字典
		FS_dict：FS坐标结构字典
		FS_bond_dict：FS成键字典

		-->IS_TF_dict:排序后的IS坐标结构字典
		-->FS_TF_dict:排序后的FS坐标结构字典
	"""
	IS_TF_dict=defaultdict(list)
	FS_TF_dict=defaultdict(list)
	for element in IS_dict.keys():
		count=len(IS_dict[element])
		ini_list=list(range(count))
		for atom_IS in IS_dict[element]:
			if(list(atom_IS.keys())[0] in IS_bond_dict.keys()):
				atom_IS_bond=(IS_bond_dict[list(atom_IS.keys())[0]])
				ini_list_bond=[]
				for index_FS in ini_list:
					atom_FS=FS_dict[element][index_FS]
					if(list(atom_FS.keys())[0] in FS_bond_dict.keys() and FS_bond_dict[list(atom_FS.keys())[0]]==atom_IS_bond):
						ini_list_bond.append(index_FS)
				if(len(ini_list_bond)==0):
					ini_list_bond=list(ini_list)
			else:
				ini_list_bond=list(ini_list)
			dists=[]
			for index_FS in ini_list_bond:
				atom_FS=FS_dict[element][index_FS]
				atom_IS_list_i=list(atom_IS.values())[0][:3]
				atom_FS_list_i=list(atom_FS.values())[0][:3]
				atom_IS_list_e=[]
				atom_FS_list_e=[]
				"""周期性边界条件"""
				for item_IS,item_FS in zip(atom_IS_list_i,atom_FS_list_i):
					item_diff=item_FS-item_IS
					if(item_diff<=0.5 and item_diff>=-0.5):
						pass
					elif(item_diff>0.5):
						item_IS+=1
					elif(item_diff<-0.5):
						item_FS+=1
					atom_IS_list_e.append(item_IS)
					atom_FS_list_e.append(item_FS)
				###--end--###
				dist=np.linalg.norm(np.array(atom_IS_list_e)-np.array(atom_FS_list_e)) #计算欧式距离
				dists.append(dist)
			#print(dists)
			index_min_FS=ini_list_bond[dists.index(min(dists))]
			IS_TF_dict[element].append(atom_IS)
			FS_TF_dict[element].append(FS_dict[element][index_min_FS])
			ini_list=[item for item in ini_list if item!=index_min_FS]
	return IS_TF_dict,FS_TF_dict

def check(IS_dict,IS_TF_dict):
	#检查距离合理性，通过计算初始和处理后原子个数
	"""
		IS_dict: 排序前IS坐标结构字典
		IS_TF_dict：排序后IS坐标结构字典
	"""
	for element in IS_dict:
		if(len(IS_dict[element])!=len(IS_TF_dict[element])):
			print("\e[1;32m 距离太小，请适当增大距离 \e[0m")
			exit()

def write(filename,head,body):
	#将排序好的结构写入IS_sort和FS_sort文件
	"""
		filename:文件名
		head：POSCAR头信息
		body：坐标字典
	"""

	with open(filename,'w') as f:
		f.writelines(head)
		for element in body.keys():
			for atom in body[element]:
				line=[str(item)+"\t" for item in list(atom.values())[0]]
				f.writelines(line)
				f.write("\n")

def main():
	"""程序主函数"""
	print("排序前：\t"+os.popen('perl ./dist.pl IS FS').read().rstrip())
	IS_head,IS_base,IS_loc_dict=load('IS')
	FS_head,FS_base,FS_loc_dict=load('FS')

	try:
		ignore_bond=sys.argv[1]
	except IndexError:
		print("Usage: nebsort C-O (i.e.)")
		ignore_bond=input("请输入需要忽略的键：")

	IS_bond_dict=bond_info(IS_base,IS_loc_dict,ignore_bond)
	FS_bond_dict=bond_info(FS_base,FS_loc_dict,ignore_bond)
	IS_TF_dict,FS_TF_dict=atom_sort(IS_loc_dict,IS_bond_dict,FS_loc_dict,FS_bond_dict)
	check(IS_loc_dict,IS_TF_dict)
	write('IS_sort',IS_head,IS_TF_dict)
	write('FS_sort',FS_head,FS_TF_dict)
	print("排序后：\t"+os.popen('perl ./dist.pl IS_sort FS_sort').read().rstrip("\n"))

if __name__ == '__main__':
	main()

#profile.run('main()','result')
#p=pstats.Stats("result")
#p.strip_dirs().sort_stats("time").print_stats()
