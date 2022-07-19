#!/usr/bin/zsh
#created at 2019/04/27
#modified at 2019/05/06 可以修改任意坐标
#功能：固定单个原子
echo -e "\e[1;31m function:Fix atom coordinate! \e[0m"
workdir=`pwd`
read -p "Please input the row and the coordinate info you want to modify:[10 F T F] " row x y z

if [[ ! "$row" =~ [0-9]+ ]];then
	echo -e "\e[1;32m Please input number! \e[0m"
	exit
fi

if [[ ! "$x" =~ [T|F] || ! "$y" =~ [T|F] || ! "$y" =~ [T|F] ]];then
	echo -e "\e[1;33m x,y,z should be [T|F]! \e[0m"
	exit
fi

for dir in `ls`
do
	if [[ -d $dir ]];then
		cd $dir
		if [ -e POSCAR ];then
			sed -i "" ${row}"s/[T|F] [T|F] [T|F]/$x $y $z/" POSCAR #unix需加空格
		else
			echo -e "\e[1;34m ${dir}/POSCAR doesn't exist! \e[0m"
			continue
		fi
		cd $workdir
		if [ -e INCAR -a -e KPOINTS -a -e POTCAR -a -e vasp.script ];then
			cp INCAR KPOINTS POTCAR vasp.script ${dir}/
		fi
	fi
done
echo -e "\e[1;31m ***************Done!*************** \e[0m"
