#!/bin/bash

egrep -v '[O|H]' OUT.ANI | egrep '[a-z|A-Z]' > temp_input
line_2nd=`cat -n temp_input | grep STEP | head -2 | tail -1  | awk '{print $1}'`
NCl=`echo "$line_2nd-3" | bc`
STEPS=`grep STEP temp_input | tail -1 | awk '{print $3}'`
cat > temp_LATT << EOF
1 0 0
0 1 0
0 0 1
EOF
bar=''
old_count=0
rm -f temp_dis
for i in `seq 1 $STEPS`
do
	for j in `seq 1 $NCl`
	do
		Clj=`echo "6*($i-1)+1+$j" | bc`
		Pt=`echo "6*$i" | bc`
		sed -n "$Clj p" temp_input | awk '{print $2,$3,$4}' > temp_XYZ
		sed -n "$Pt p" temp_input | awk '{print $2,$3,$4}' >> temp_XYZ
		~/scripts/distance temp_LATT temp_XYZ >> temp_dis		
	done
	count=$[$i*100/$STEPS]
	printf "Processing:[%-100s][%d%%]\r" "$bar" $count
	if [ $count -gt $old_count ];then
		bar+='='
		let old_count++
	fi
done
printf "\n"

cat temp_dis | awk '{if(NR%4==0){print $0} else {printf "%s",$0}}'> temp_dis_formed
