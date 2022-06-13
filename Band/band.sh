#!/usr/bin/bash

bandn=`sed -n '6p' EIGENVAL | gawk '{print $3}'`
for (( i = 1; i <= $bandn; i++ ))
	do
		gawk "/^\s+${i}\s+-?[0-9]+\./{print $1}" EIGENVAL | gawk '{printf "%10s\n",($2+$3)/2}' >> $i.log
		rm $i.log
	done
