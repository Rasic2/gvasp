#!/usr/bin/env python
# -*- coding:utf-8 -*-
#用于CI-NEB计算中IS与FS结构调整
# created by hui_zhou@mail.ecust.edu.cn at 2019/07/16
# modified at 2019/07/18 修改确认相同原子算法
# modified at 2019/07/30 修改算法，添加PBC（周期性边界条件规则）
# modified at 2019/12/21 修改算法，遗传算法+距离双排序
#<--Version:0.0.5-->

import os
import math
import random
import numpy as np
from collections import defaultdict,Counter

#import profile,pstats
#from fortfunc import fort_floor as floor

def load(filename):
	"""加载IS、FS结构，返回结构头文件和坐标字典"""
	with open(filename) as f:
		file=f.readlines()
	head=file[:9]
	base=[[float(item) for item in line.split()] for line in head[2:5]]
	loc_dict=defaultdict(list)
	ele_name,ele_num=file[5].split(),file[6].split()
	pos_list=[]
	start=9
	for key,num in zip(ele_name,ele_num):
		i=1
		for line in file[start:start+int(num)]:
			loc=[float(item) if index < 3 else item for index,item in enumerate(line.split())]
			pos=loc[:3]
			name=str(key)+str(i)
			loc_dict[key].append({name:loc})
			pos_list.append(pos)
			i+=1
			start+=1
	pos_arr=np.array(pos_list)
	ele_num=np.array(ele_num).astype(int)
	return head,base,ele_num,loc_dict,pos_arr

def dist(base_IS,pos_arr_IS,pos_arr_FS):
	pos_diff=pos_arr_IS-pos_arr_FS
	pos_diff_pbc=np.where(pos_diff>0.5,pos_diff-1,pos_diff)
	pos_diff_pbc=np.where(pos_diff_pbc<-0.5,pos_diff_pbc+1,pos_diff_pbc)
	pos_diff_pbc_coord=np.dot(pos_diff_pbc,base_IS)
	return np.sqrt(np.sum(pos_diff_pbc_coord**2))

def perm(elenum_arr):
	perm_list=[]
	index=0
	for i in range(len(elenum_arr)):
		perm_list+=list(np.random.permutation(elenum_arr[i])+index)
		index+=(elenum_arr[i])
	return np.array(perm_list)

def write(filename,head,body):
	"""将排序好的结构写入IS_sort和FS_sort文件"""
	with open(filename,'w') as f:
		f.writelines(head)
		for element in body.keys():
			for atom in body[element]:
				line=[str(item)+"\t" for item in list(atom.values())[0]]
				f.writelines(line)
				f.write("\n")

def sort_dist(IS_dict,FS_dict):
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

def split(elenum_arr,base_IS,pos_arr_IS,pos_arr_FS):
	elements=np.array([i+1 for i in range(len(elenum_arr)) for item in range(elenum_arr[i])])
	pos_arr_FS_sortZ_index=np.argsort(pos_arr_FS[:,2])[:np.sum(elenum_arr)-np.sum(elenum_arr)]
	elements[pos_arr_FS_sortZ_index]=0
	pos_arr_IS_sortZ=(pos_arr_IS[np.where(elements!=0)])
	pos_arr_FS_sortZ=(pos_arr_FS[np.where(elements!=0)])
	length_ori=dist(base_IS,pos_arr_IS[np.where(elements==0)],pos_arr_FS[np.where(elements==0)])
	return elements,length_ori,pos_arr_IS_sortZ,pos_arr_FS_sortZ

def sort_genetic(elements_ori,elenum_ori,length_ori,base_IS,pos_arr_IS,pos_arr_FS,loc_dict_FS):
	elements=elements_ori[np.where(elements_ori!=0)]
	elenum_arr=list(Counter(elements).values())
	NP=200;D=np.sum(elenum_arr);Pc=0.7;Pm=0.3;G=300
	f=np.zeros(shape=(NP,D))
	nf=np.zeros(shape=(NP,D))
	for i in range(NP):
		f[i,:]=perm(elenum_arr)
	f[0]=np.arange(D)
	f=f.astype(int)
	length=np.array([dist(base_IS,pos_arr_IS,pos_arr_FS[f[i]]) for i in range(NP)])
	MSLL=np.argsort(length) #按升序排列好之后对应索引值
	Sortf=f[MSLL,:]
	trace=np.zeros(shape=G)
	for gen in range(G):
		#君主方案进行交叉操作
		Emper=Sortf[0,:] #适应度最高认为是君主
		NoPoint=int(round(D*Pc)) #交叉基因个数
		PoPint=np.random.randint(0,D,size=(int(NP/2),NoPoint)) #交叉基因数组
		nf=np.array(list(Sortf))
		for i in range(int(NP/2)):
			nf[2*i,:]=Emper #奇数子代为雄性君主
			nf[2*i+1,:]=Sortf[2*i+1,:] #偶数子代为雌性
			for k in range(NoPoint):
				if(elements[nf[2*i+1,PoPint[i,k]]]==elements[nf[2*i,PoPint[i,k]]]):
					x=np.where(nf[2*i]==nf[2*i+1,PoPint[i,k]])
					y=np.where(nf[2*i+1]==nf[2*i,PoPint[i,k]])
					nf[2*i,PoPint[i,k]],nf[2*i+1,PoPint[i,k]]=nf[2*i+1,PoPint[i,k]],nf[2*i,PoPint[i,k]] #君主与偶数第一位交叉,两个后代,奇数位为君主+交叉过来的偶数部分
					nf[2*i,x],nf[2*i+1,y]=nf[2*i+1,y],nf[2*i,x] #偶数位为偶数+交叉过来的君主部分
		#变异操作
		for m in range(NP):
			r=random.random()
			if(r<Pm):
				p1=math.floor(D*random.random())
				p2=math.floor(D*random.random())
				while(p1==p2):
					p1=math.floor(D*random.random())
					p2=math.floor(D*random.random())
				if(elements[nf[m,p1]]==elements[nf[m,p2]]):
					nf[m,p1],nf[m,p2]=nf[m,p2],nf[m,p1] #交换p1、p2进行变异
		#子代父代合并,选取前NP个个体
		length_new=np.array([dist(base_IS,pos_arr_IS,pos_arr_FS[nf[i]]) for i in range(NP)])
		SortfMSLL=np.argsort(np.concatenate((length,length_new)))[:NP]
		Sortf=np.concatenate((Sortf,nf))[SortfMSLL,:]
		length=np.array([dist(base_IS,pos_arr_IS,pos_arr_FS[Sortf[i]]) for i in range(NP)])
		trace[gen]=math.sqrt(length[0]**2+length_ori**2)
		print(gen,"\t",trace[gen])

	#返回排序后的字典
	elenum_index_ori=np.array(list(range(len(elements_ori))))
	elenum_sortZ_index_ori=elenum_index_ori[np.where(elements_ori!=0)]
	elenum_sortZ_index_current=elenum_sortZ_index_ori[Sortf[0]]
	elenum_index_current=np.where(elements_ori==0,elenum_index_ori,None)
	elenum_index_current[np.where(elenum_index_current==None)]=elenum_sortZ_index_current

	Bestf=elenum_index_current
	sort_dict_FS=defaultdict(list)
	start=0
	for element,i in zip(loc_dict_FS.keys(),range(len(elenum_ori))):
		end=np.cumsum(elenum_ori)[i]
		for sort_index in Bestf[start:end]:
			sort_dict_FS[element].append(loc_dict_FS[element][sort_index-start])
		start+=elenum_ori[i]
	return sort_dict_FS

def main():
	"""双排序算法"""
	os.system('perl ./dist.pl IS FS')
	head_IS,_,_,loc_dict_IS,_=load('IS')
	head_FS,_,_,loc_dict_FS,_=load('FS')
	TF_dict_IS,TF_dict_FS=sort_dist(loc_dict_IS,loc_dict_FS)
	write('IS_sort',head_IS,TF_dict_IS)
	write('FS_sort',head_FS,TF_dict_FS)

	os.system('perl ./dist.pl IS_sort FS_sort')
	head_IS,base_IS,elenum_IS,loc_dict_IS,pos_arr_IS=load('IS_sort')
	head_FS,base_FS,elenum_FS,loc_dict_FS,pos_arr_FS=load('FS_sort')
	elements,length_ori,pos_arr_IS_sortZ,pos_arr_FS_sortZ=split(elenum_FS,base_IS,pos_arr_IS,pos_arr_FS)
	sort_dict_FS=sort_genetic(elements,elenum_FS,length_ori,base_IS,pos_arr_IS_sortZ,pos_arr_FS_sortZ,loc_dict_FS)
	write('IS_sort',head_IS,loc_dict_IS)
	write('FS_sort',head_FS,sort_dict_FS)
	os.system('perl ./dist.pl IS_sort FS_sort')

if __name__ == '__main__':
	main()

#profile.run('main()','result')
#p=pstats.Stats("result")
#p.strip_dirs().sort_stats("time").print_stats()

