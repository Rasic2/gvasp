#/usr/bin/bash
#created by hui_zhou@mail.ecust.edu.cn 2019/05/12
#-->Version:0.1.1<--

workdir=`pwd`
a=`python3 lattice.py | sed -n '2'p | awk '{printf"%.5f", $3} '`
b=`python3 lattice.py | sed -n '3'p | awk '{printf"%.5f", $3} '`
c=`python3 lattice.py | sed -n '4'p | awk '{printf"%.5f", $3} '`
alpla=`python3 lattice.py | sed -n '5'p | awk '{printf"%.5f",  $3} '`
beta=`python3 lattice.py | sed -n '6'p | awk '{printf"%.5f",  $3} '`
gamma=`python3 lattice.py | sed -n '7'p | awk '{printf"%.5f",  $3} '`
for file in *.xyz
do
	name=${file%.*}
	rm ${name}.arc
	echo "!BIOSYM archive 3">> ${name}.arc
	echo "PBC=ON" >> ${name}.arc
	lineno=`grep 'create form python' ${name}.xyz | wc -l`
	elemno=`head -1 ${name}.xyz | awk '{print $1}'`
	for frame in `seq $lineno`
	do
		echo "Auto Generated CAR File" >> ${name}.arc
		echo "!DATE `date | sed 's/CST / /g'`" >> ${name}.arc
		echo "PBC   $a  $b  $c  $alpla  $beta  $gamma (P1)" >> ${name}.arc
		start=$[$frame * ($elemno + 2) - $elemno + 1]
		end=$[$frame * ($elemno +2) ]
		sed -n "$start,$end p" ${name}.xyz | awk '{printf "%-5s %14.9f %14.9f %14.9f XXXX 1       xx     %-2s 0.0000\n",$1NR,$2,$3,$4,$1}' >> ${name}.arc
		echo "end" >> ${name}.arc
		echo "end" >> ${name}.arc
	done
	rm ${name}.xyz
done
