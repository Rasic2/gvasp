#!/usr/bin/env python
import os

row=input("Please input row: ")
info=input("please input which coordinate you want to fix:[FTF]")
workdir=os.popen('pwd').read().rstrip()
dirs=[name for name in os.listdir(workdir) if os.path.isdir(workdir+'/'+name)]
for dir_ in dirs:
	os.system("sed -i {0}'s/T T T/{1} {2} {3}/' {4}".format(row,info[0],info[1],info[2],dir_+'/POSCAR'))