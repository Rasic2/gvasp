#!/usr/bin/env python
#用于CI-NEB计算中IS与FS结构调整
# created by hui_zhou@mail.ecust.edu.cn,2019/07/16
# modified at 2019/07/18 修改确认相同原子算法
# modified at 2019/07/30 修改算法，添加PBC（周期性边界条件规则）
# <--Version:0.1.5-->

import numpy as np
from collections import defaultdict

def load(filename):
	"""加载IS、FS结构，返回结构头文件和坐标字典"""
	with open(filename) as f:
		file=f.readlines()
	head=file[:9]
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
	return head,loc_dict

def atom_sort(IS_dict,FS_dict):
	"""对IS、FS坐标重新排序，考虑周期性边界条件下，最小原子距离认为是同一个原子"""
	IS_TF_dict=defaultdict(list)
	FS_TF_dict=defaultdict(list)
	for element in IS_dict.keys():
		count=len(IS_dict[element])
		ini_list=list(range(count))
		for atom_IS in IS_dict[element]:
			dists=[]
			for index_FS in ini_list:
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
			index_min_FS=ini_list[dists.index(min(dists))]
			IS_TF_dict[element].append(atom_IS)
			FS_TF_dict[element].append(FS_dict[element][index_min_FS])
			ini_list=[item for item in ini_list if item!=index_min_FS]
	return IS_TF_dict,FS_TF_dict

def check(IS_dict,IS_TF_dict):
	"""检查距离合理性，通过计算初始和处理后原子个数"""
	for element in IS_dict:
		if(len(IS_dict[element])!=len(IS_TF_dict[element])):
			print("\e[1;32m 距离太小，请适当增大距离 \e[0m")
			exit()

def write(filename,head,body):
	"""将排序好的结构写入IS_sort和FS_sort文件"""
	with open(filename,'w') as f:
		f.writelines(head)
		for element in body.keys():
			for atom in body[element]:
				line=[str(item)+"\t" for item in list(atom.values())[0]]
				f.writelines(line)
				f.write("\n")

def main():
	"""程序主函数"""
	IS_head,IS_dict=load('IS')
	FS_head,FS_dict=load('FS')
	IS_TF_dict,FS_TF_dict=atom_sort(IS_dict,FS_dict)
	check(IS_dict,IS_TF_dict)
	write('IS_sort',IS_head,IS_TF_dict)
	write('FS_sort',FS_head,FS_TF_dict)

if __name__ == '__main__':
	main()
