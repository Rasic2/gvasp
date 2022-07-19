#!/bin/bash

# Variable: [python3] --> the path of python.exe

dispy()
{
	cat > MD_dis.py << EOF
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
EOF
}

# python3=/home/apps/intel/intelpython3/bin/python3
python3=python3
if [ "$1x" == "x" ];then
	dis=2.5
else
	dis=$1
fi
egrep -v '[O|H]' OUT.ANI | egrep '[a-z|A-Z]' > temp_input
grep -v 'STEP' temp_input | awk '{print $2,$3,$4}' > temp_input_2
line_2nd=`cat -n temp_input | grep STEP | head -2 | tail -1  | awk '{print $1}'`
NCl=`echo "$line_2nd-3" | bc`
STEPS=`grep STEP temp_input | cat -n | tail -1 | awk '{print $1}'`

dispy
$python3 `pwd`/MD_dis.py $NCl $STEPS
rm MD_dis.py

paste temp_dis* > temp_form_dis
cat -n temp_form_dis | awk '{for(i=2;i<=NF;i++){if($i>='"$dis"'){printf "%s\t Cl_%d\n",$0,(i-1)}}}' > dis_form_result
col=$[$NCl+2]
sort -k $col -k1n,1 dis_form_result > dis_sort_form_result

awk '{for(j=2;j<NF;j++){a[NR,j]=$j;b[NR]=$NF;c[NR]=$1;}}END{for(i=2;i<NR;i++){for(j=2;j<NF;j++){k=j-1;if(a[i,j]>a[i-1,j] && a[i,j]>a[i+1,j] && a[i,j]>="'$dis'" && b[i]~k){printf "%d\t %d\t %s\n",i,c[i],b[i];}}}}' dis_sort_form_result > dis_count

for i in `seq 1 $NCl`
do
	Cl_n=`grep "Cl_$i" dis_count | wc -l`
	echo -e "The count of \033[1;33mPt-Cl_$i\033[0m whose distance over than $dis is: \033[1;31m$Cl_n\033[0m"
done

mv temp_form_dis dis_result
rm -rf temp_* 
