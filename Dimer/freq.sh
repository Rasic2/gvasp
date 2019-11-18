#!/bin/bash
#created by 周慧，2019/05/07
#function:从OUTCAR提取虚频文件

image=`grep "Hz" OUTCAR | grep 'f/i'`
image_count=`grep "Hz" OUTCAR | grep 'f/i' | wc -l`
if [ $image_count -gt 0 ];then
	echo -e "\e[1;31m 虚频个数为：$image_count \e[0m"
	echo $image | tee image
else
	echo -e "\e[1;32m 该结构不存在虚频！ \e[0m"
	exit
fi

element_count=`sed -n '7p' POSCAR | awk '{print $1+$2+$3}'`
if [ $? -eq 0 ];then
	echo -e "\e[1;33m 元素个数为：$element_count \e[0m"
else
	echo -e "\e[1;31m POSCAR 格式错误！ \e[0m"
	exit
fi

while read line
do
	num=`echo $line | awk '{print $1}'`
	pattern=`echo $line | awk -F= '{print $1}'`
	start=`grep -n "$pattern" OUTCAR | awk -F: '{print $1}'`
	end=$[$start + $element_count + 1]
	sed -n "$start,$end p" OUTCAR > freq$num
	python3 freqmov.py freq$num 30 0.6
done < image
bash xyz_arc.sh

rm -rf image
