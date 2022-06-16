#!/bin/bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
	cat >temp_x2p_help <<EOF

[34m#########################################################################
# File Name: xsd2pos.sh
# Author: wdhu; hzhou
# Created Time: Mon 22 Dec 2014 11:54:27 PM CST
# Modified Time: Wed Apr 27 13:19:00 CST 2022 
#########################################################################
[0m
creat the POSCAR POTCAR... according to the xsdfiles;
the format of POSCAR outfile is vasp5 format.
the POTCAR created need the Pseudopotential Library;
the INCAR job.script created or updated need the old files in \$HOME/example or work dir.
the # in INCAR would not replace.
you can set some parameters by .setting_xsd2pos in home directory or work directory; or set from script ARGVs.
the priority of parameters is (1)script ARGVs; (2).setting_xsd2pos in work directory; (3).setting_xsd2pos in home directory.

Examples                               Choices
[31m cpot=1 [0m                          [34m #0:don't create POTCAR;not 0:create POTCAR [0m
[31m cscript=1  [0m                      [34m #0:don't update vasp.script;not 0:update; -1 auto [0m
[31m ckpoint=-1 [0m                      [34m #0:don't create KPOINTS;not 0:create KPOINTS; -1: auto[0m
[31m setmag=1 [0m                        [34m #0:don't set MAGMOM in INCAR;not 0:set MAGMOM; -1: auto [0m
[31m setpU=1  [0m                        [34m #0:don't set DFT plus U; not 1:set DFT+U; -1: auto [0m
[31m sortZ=1  [0m                        [34m #0:sort default ; not 0: sort by Z axis [0m
[31m posfm=5  [0m                        [34m #the Format of POSCAR: 4 or 5 [0m
[31m cmark=_c  [0m                       [34m #Constrainmark: _c(default) [0m
[31m potmode=new [0m                     [34m #new, ori, sv, pv ,GW or Custom  [0m
[31m incell=0 [0m                        [34m #the XYZ positions convert into cell; 1: yes;0;not [0m
[31m potdir=\$HOME/pot/potpaw_PBE2010 [0m [34m #Pseudopotential Library directory [0m
[31m examdir=\$HOME/example [0m           [34m #examples directory [0m
[31m pUdir=\$HOME/script/Uvalue [0m       [34m #the dir that save U parameters [0m
[31m inmode=opt [0m                      [34m #opt, chg, dos, freq[0m
[31m lowmode=no [0m                      [34m #low accuracy calculations, i.e., ENCUT=300[0m
[31m gammode=no [0m                      [34m #gamma-point calculation[0m
[31m solmode=no [0m                      [34m #solvation effect calculation[0m
[31m hsemode=no [0m                      [34m #HSE06calculation[0m
[31m nelectmode=no [0m                   [34m #NELECT set[0m

The Argv setting
You can set the parameters like the examples above.

[33;1mIf you have any problem or find any BUGs, please contact with me.[0m

EOF
	cat temp_x2p_help
	rm -rf temp_x2p_help
	exit 0
fi
rm -rf temp_x2p_*

# default paramenters
IMAGES=4
ppn=20
node=1
cpot=1
cscript=1
ckpoint=-1
setmag=1
setpU=1
incell=0
posfm=5
inmode=opt
potmode=ori
nelectmode=no
gammamode=no
solmode=no
hsemode=no
vdwmode=no
lowmode=no
potdir=$HOME/pot/PAW_PBE/
examdir=$HOME/example/PBE
pUdir=$HOME/Uvalue
cmark=_c
sortZ=1 #>0:sort by atoms Z axis; 0: only sort by atom element name.
potcfgdir=$HOME
jobscript=vasp.script

workdir=$(pwd)

echo -e "\n  >>>>>>>>>>>>>>>>>> Check Information <<<<<<<<<<<<<<<<<<\n"
# import the setting files
cd $HOME
if [[ -f .setting_xsd2pos ]]; then
	sed -i 's/ //g' .setting_xsd2pos
	. .setting_xsd2pos
	echo -e "    Read setting in home directory."
fi
cd $workdir
if [[ -f .setting_xsd2pos ]]; then
	sed -i 's/ //g' ./.setting_xsd2pos
	. ./.setting_xsd2pos
	echo -e "    Read setting in work directory."
	echo -e "    (\033[35;1m$DIRSTACK\033[0m)"
fi

# read ARGV
until [[ $# -eq 0 ]]; do
	if [[ $1 =~ "=" ]]; then
		argvs1=$(echo $1 | awk -F = '{print $1}')
		argvs2=$(echo $1 | awk -F = '{print $2}')
		if [ -z "$argvs1" -o -z "$argvs2" ]; then
			echo -e "     Error in Read ARGV, Exit!!!  "
			exit
		fi
		eval $argvs1=$argvs2
	elif [[ $1 == "PW91" ]]; then
		potdir=~/POT/PAW_PW91/
		examdir=~/example
	elif [[ "$1" =~ "N"[+-][0-9]* ]]; then
		nelectmode=$1
	elif [[ $1 == "new" ]]; then
		potmode=new
	elif [[ $1 == "ori" ]]; then
		potmode=ori
	elif [[ $1 == "pv" ]]; then
		potmode=pv
	elif [[ $1 == "sv" ]]; then
		potmode=sv
	elif [[ $1 == "GW" ]]; then
		potmode=GW
	elif [[ $1 == "Custom" ]]; then
		potmode=Custom
	elif [[ $1 == "custom" ]]; then
		potmode=Custom
	elif [[ $1 == "cus" ]]; then
		potmode=Custom
	elif [[ $1 == "sortZ" ]]; then
		sortZ=1
	elif [[ $1 == "sortN" ]]; then
		sortZ=0
	elif [[ $1 == "incell" ]]; then
		incell=1
	elif [[ $1 == "chg" ]]; then
		inmode=chg
		cp $examdir/INCAR_chg ./INCAR
		echo -e "\e[1;32m \t\t\t电荷密度计算 \n\e[0m"
	elif [[ $1 == "freq" ]]; then
		inmode=freq
		cp $examdir/INCAR_freq ./INCAR
		echo -e "\e[1;32m \t\t\t频率计算 \n\e[0m"
	elif [[ $1 == "TS" ]]; then
		inmode=TS
		cp $examdir/INCAR_TS ./INCAR
		echo -e "\e[1;32m \t\t\t过渡态计算 \n\e[0m"
	elif [[ $1 == "DOS" || $1 == "dos" ]]; then
		inmode=DOS
		cp $examdir/INCAR_DOS ./INCAR
		echo -e "\e[1;32m \t\t\tDOS计算 \n\e[0m"
	elif [[ $1 == "NEB" || $1 == "neb" ]]; then
		inmode=NEB
		cp $examdir/INCAR_NEB ./INCAR
		echo -e "\e[1;32m \t\t\tNEB计算 \n\e[0m"
	elif [[ $1 == "CINEB" || $1 == "cineb" ]]; then
		inmode=CINEB
		cp $examdir/INCAR_NEB ./INCAR
		echo -e "\e[1;32m \t\t\tCI-NEB计算 \n\e[0m"
	elif [[ $1 == "dimer" || $1 == "Dimer" ]]; then
		inmode=dimer
		cp $examdir/INCAR_dimer ./INCAR
		echo -e "\e[1;32m \t\t\tDimer过渡态计算 \n\e[0m"
	elif [[ $1 == "MD" || $1 == "md" ]]; then
		inmode=MD
		cp $examdir/INCAR_MD ./INCAR
		echo -e "\e[1;32m \t\t\t分子动力学计算 \n\e[0m"
	elif [[ $1 == "gamma" || $1 == "G" ]]; then
		gammamode=yes
	elif [[ $1 == "SOL" ]]; then
		solmode=yes
	elif [[ $1 == "HSE" || $1 == "hse" ]]; then
		hsemode=yes
		setpU=0
	elif [[ $1 == "VDW" || $1 == "vdw" ]]; then
		vdwmode=yes
	elif [[ $1 == "Low" || $1 == "low" || $1 == "L" ]]; then
		lowmode=yes
	fi
	shift
done

xsdfile=$(ls *.xsd 2>/dev/null | head -1)
if [ ! -f "$xsdfile" ]; then
	rz #2>&1 > /dev/null
fi
if [ ! -f "$xsdfile" ]; then
	exit 0
fi
xsdfile=$(ls *.xsd 2>/dev/null | head -1)

echo -e "\e[1;31m"
echo $potdir | awk -F/ '{print "所用赝势为："$8}'
echo -e "\e[0m"

if [[ $inmode == "opt" ]]; then
	echo -e "\e[1;32m \t\t\t结构优化计算 \n\e[0m"
fi

if [[ -f "$xsdfile" ]]; then
	echo -e "    The xsdfile is : \033[31;1;4m$xsdfile\033[0m \n"
else
	echo -e "    The xsdfile($xsdfile) do not exist!!!"
	exit 0
fi

elementlist="	H He\
				Li Be  B  C  N  O  F Ne\
				Na Mg Al Si  P  S Cl Ar\
				 K Ca Sc Ti  V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr\
				Rb Sr  Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te  I Xe\
				Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Hf Ta  W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn\
				Fr Ra Ac Th Pa  U Np Pu An Cm Bk Cf Es Fm Md No Rf Db Sg Bh Hs Mt Ds Rg Cn Uut Uuq Uup Uuh Uus Uuo End"
if [[ "$(grep Atom3d $xsdfile | grep Components | wc -l)" == 0 ]]; then
	echo -e "    None elements information in $xsdfile file. Exit!\n    You can try \"xsd2pos -h\" for help!!!"
fi

grep Atom3d $xsdfile | grep Components | awk -F Name=\" '{print$2}' | awk -F \" '{print $1}' >temp_x2p_Name &
grep Atom3d $xsdfile | grep Components | awk -F Components=\" '{print$2}' | awk -F \" '{print $1}' | sed 's/,.*[0-9]//g' >temp_x2p_Element &
grep Atom3d $xsdfile | grep Components | awk -F Components=\" '{print$2}' | awk -F \" '{print $1}' | sed 's/,//g;s/[a-Z]//g' >temp_x2p_Iso &
grep Atom3d $xsdfile | grep Components | awk -F FormalSpin=\" '{print$2}' | awk -F \" '{print $1+0}' | sed 's/00//g' >temp_x2p_Spin &
if [[ "$incell" -eq 1 ]]; then
	grep Atom3d $xsdfile | grep Components | awk -F XYZ=\" '{print$2}' | awk -F \" '{print $1}' |
		awk -F \, '{printf"%18.12f%18.12f%18.12f\n",$1-($1<0?int($1-1):int($1)),$2-($2<0?int($2-1):int($2)),$3-($3<0?int($3-1):int($3))}' >temp_x2p_XYZ &
else
	grep Atom3d $xsdfile | grep Components | awk -F XYZ=\" '{print$2}' | awk -F \" '{print $1}' | awk -F \, '{printf"%18.12f%18.12f%18.12f\n",$1,$2,$3}' >temp_x2p_XYZ &
fi
grep Atom3d $xsdfile | grep Components | awk -F RestrictedProperties=\" '{print$2}' | awk -F \" '{if($1=="FractionalXYZ"){print "F   F   F"}else{print "T   T   T"}}' >temp_x2p_TF &
grep SpaceGroup $xsdfile | awk -F Vector '{printf"%s\n%s\n%s\n",$2,$3,$4}' | awk -F"\"|," '{printf "% 14.8f %14.8f %14.8f\n",$2,$3,$4}' >temp_x2p_lattice &

wait

if [[ "$sortZ" -gt 0 ]]; then
	paste -d: temp_x2p_Element temp_x2p_Name temp_x2p_XYZ temp_x2p_TF temp_x2p_Spin temp_x2p_Iso | awk -F: '{printf"%s:%s\n",  match("'"$elementlist"'",$1),$0}' | sort -n -t: -k1 -k7 -k6 -k4.38,4.46 -k4.21,4.28 | grep -n : >temp_x2p_tot
else
	paste -d: temp_x2p_Element temp_x2p_Name temp_x2p_XYZ temp_x2p_TF temp_x2p_Spin temp_x2p_Iso | awk -F: '{printf"%s:%s\n",  match("'"$elementlist"'",$1),$0}' | sort -n -t: -k1 -k7 -s | grep -n : | sort -t: -k3 -k7 >temp_x2p_tot
fi

# shortinfo
awk -F ':' '{print $3,$7+0,$3""$7+0}' temp_x2p_tot | uniq -c >temp_x2p_Elenum
awk -F ':' '{printf" %s %s %s\n", $3,$6,$7+0}' temp_x2p_tot | awk '{printf" %s%s  %s%s%s\n",$1,$5,$2,$3,$4}' >temp_x2p_EleTF
rm -f temp_x2p_shortinfo
for i in $(cat temp_x2p_Elenum | awk '{print $4}'); do
	echo "$(grep -w $i temp_x2p_Elenum | awk '{printf "%s %s %d\n", $2,$3,$1}') $(grep -w $i temp_x2p_EleTF | grep TTT | wc -l) $(grep -w $i temp_x2p_EleTF | grep FFF | wc -l)" >>temp_x2p_shortinfo
done
echo -e "    \033[4m Element       Numbers      \033[0m"
awk 'BEGIN{t=0;f=0;tot=0};{printf"     %3s %3s \033[1;33m%4d\033[0m\033[32m%4d\033[0m(T)\033[31m%4d\033[0m(F)\n",$1,$2,$3,$4,$5}{t+=$4;f+=$5;tot+=$3};END{printf"     ___________________________\n      Total  \033[1;33m%4d\033[0m\033[32m%4d\033[0m(T)\033[31m%4d\033[0m(F)\n",tot,t,f}' temp_x2p_shortinfo

# creat POSCAR
echo -e "AutoCreatByScript: $(awk '{if($2==0){printf"%s ",$1}else{printf"%s ", $1$2}}' temp_x2p_shortinfo)\n1.000000000" >POSCAR
cat temp_x2p_lattice >>POSCAR
awk '{printf "%5s", $1}END{printf"\n"}' temp_x2p_shortinfo >>POSCAR
awk '{print $3}' temp_x2p_shortinfo | awk '{printf "%5d",$1}END{printf"\n"}' >>POSCAR
echo -e "Selective Dynamics\nDirect" >>POSCAR
awk -F : '{printf"%s    %s\n", $5, $6}' temp_x2p_tot >>POSCAR
if [[ "$posfm" == 4 ]]; then
	sed -i 6d POSCAR
fi
# creat fort.188
grep -i "$cmark" temp_x2p_tot | sed 's/:/ /g;s/\t/ /g;s/  / /g' | awk '{printf"%3s %-2s %-5s%10.6f%10.6f%10.6f  %s %s %s\n",$1,$3,$4,$5,$6,$7,$8,$9,$10}' >temp_x2p_Constrain
if [[ -f temp_x2p_Constrain ]]; then
	nc=$(cat temp_x2p_Constrain | wc -l)
else
	nc=0
fi
if [[ "$nc" -eq 2 ]]; then
	awk '{printf "%f %f %f ",$4,$5,$6}' temp_x2p_Constrain >temp_x2p_ConstrainXYZ
	dis=$($(dirname $0)/distance temp_x2p_lattice temp_x2p_ConstrainXYZ | awk '{printf"%.5f", $1}')
	if [[ ! -f "fort.188" ]]; then
		echo -e "1\n3\n6\n3\n0.03\n$(awk '{printf "%d   ",$1}' temp_x2p_Constrain)  $dis\n0" >"fort.188"
	else
		sed -n '1,5'p fort.188 >temp_x2p_fort188
		echo -e "$(awk '{printf "%d   ",$1}' temp_x2p_Constrain)  $dis\n0" >>temp_x2p_fort188
		mv temp_x2p_fort188 fort.188
	fi
	echo -e "\n    find two contrained atoms, shift to TS mode :"
	cat temp_x2p_Constrain | awk '{printf "    %s\n",$0}'
	echo -e "    Its distance : \033[33;1m$(echo $dis)\033[0m"
	echo -e "    Creat fort.188 successfully ! \n"
elif [[ "$nc" == 0 ]]; then
	echo ""
else
	echo -e "\n    find $nc contrained atom(s), fort.188 don't Creat !\n"
fi

# spin set
if [[ "$setmag" == -1 ]]; then
	if [[ -f INCAR ]]; then
		setmag=1
	else
		setmag=0
	fi
fi
if [[ "$setmag" -gt 0 ]]; then
	if [[ ! -f INCAR ]]; then
		cp $examdir/INCAR .
	fi

	magmomtag=$(awk -F : '{print $7 }' temp_x2p_tot | uniq -c | awk '{printf " %d*%d",$1,$2}')
	if [[ $(grep ISPIN INCAR | awk -F \# '{print $1}' | awk -F = '{print$2}' | sed 's/ //g') == 2 ]]; then
		sed -i 's/MAGMOM *=.*/MAGMOM ='"$magmomtag"' #magnetic/' INCAR
		if [[ "$(grep MAGMOM INCAR | awk -F \# '{print $1}')" ]]; then
			echo -e "    The MAGMOM-tag has set !"
			echo -e "    $(grep MAGMOM INCAR | awk -F \# '{print $1}')"
		else
			echo -e "    The MAGMOM-tag do not take effect !!"
		fi
	else
		echo -e "    the ISPIN-tag isn't set to 2 !!"
	fi
fi
# creat POTCAR
if [[ "$cpot" -gt 0 ]]; then
	if [[ -d "$potdir" ]]; then
		rm -f POTCAR temp_x2p_potlog
		if [[ "$potmode" == "new" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				if [[ -f $potdir/"$i"_new/POTCAR ]]; then
					cat $potdir/"$i"_new/POTCAR >>POTCAR
					echo ''$i'_new ' >>temp_x2p_potlog
				else
					cat $potdir/"$i"/POTCAR >>POTCAR
					echo "$i " >>temp_x2p_potlog
				fi
			done
		elif [[ "$potmode" == "sv" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				if [[ -f $potdir/"$i"_sv_new/POTCAR ]]; then
					cat $potdir/"$i"_sv_new/POTCAR >>POTCAR
					echo ''$i'_sv_new ' >>temp_x2p_potlog
				elif [[ -f $potdir/"$i"_sv/POTCAR ]]; then
					cat $potdir/"$i"_sv/POTCAR >>POTCAR
					echo ''$i'_sv ' >>temp_x2p_potlog
				else
					cat $potdir/"$i"/POTCAR >>POTCAR
					echo "$i " >>temp_x2p_potlog
				fi
			done
		elif [[ "$potmode" == "pv" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				if [[ -f $potdir/"$i"_pv_new/POTCAR ]]; then
					cat $potdir/"$i"_pv_new/POTCAR >>POTCAR
					echo ''$i'_pv_new ' >>temp_x2p_potlog
				elif [[ -f $potdir/"$i"_pv/POTCAR ]]; then
					cat $potdir/"$i"_pv/POTCAR >>POTCAR
					echo ''$i'_pv ' >>temp_x2p_potlog
				else
					cat $potdir/"$i"/POTCAR >>POTCAR
					echo "$i " >>temp_x2p_potlog
				fi
			done
		elif [[ "$potmode" == "GW" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				if [[ -f $potdir/"$i"_GW/POTCAR ]]; then
					cat $potdir/"$i"_GW/POTCAR >>POTCAR
					echo ''$i'_GW ' >>temp_x2p_potlog
				else
					if [[ $(ls $potdir/"$i"*_GW/POTCAR 2>/dev/null) ]]; then
						ls $potdir/"$i"*_GW/POTCAR | head -1 | xargs cat >>POTCAR
						echo "$(ls $potdir/"$i"*_GW/POTCAR | head -1 | awk -F/ '{print $(NF-1)}') " >>temp_x2p_potlog
					else
						cat $potdir/"$i"/POTCAR >>POTCAR
						echo "$i " >>temp_x2p_potlog
					fi
				fi
			done
		elif [[ "$potmode" == "Custom" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				potname=$(grep -w $i $potcfgdir/.potcfg | awk '{print $2}')
				if [[ -f $potdir/"$potname"/POTCAR ]]; then
					cat $potdir/"$potname"/POTCAR >>POTCAR
					echo "$potname " >>temp_x2p_potlog
				else
					cat $potdir/"$i"/POTCAR >>POTCAR
					echo "$i " >>temp_x2p_potlog
				fi
			done
		elif [[ "$potmode" == "ori" ]]; then
			for i in $(awk '{print $1}' temp_x2p_shortinfo); do
				if [[ "$i" == "Zr" || "$i" == "Y" || "$i" == "Sr" || "$i" == "K" ]]; then
					cat $potdir/"$i"_sv/POTCAR >>POTCAR
				elif [[ "$i" == "Ca" ]]; then
					cat $potdir/"$i"_pv/POTCAR >>POTCAR
				else
					cat $potdir/"$i"/POTCAR >>POTCAR
				fi
				echo "$i " >>temp_x2p_potlog
			done
		fi
		echo -e "    The POTCAR Created! The Elements is : "
		echo -e "    (\033[1;35m$(cat temp_x2p_potlog | xargs)\033[0m)\n"
	else
		echo -e "    The POTCAR folder ($potdir) is nonexistent!!!"
	fi
fi
# creat KPOINTS
if [[ "$ckpoint" == -1 ]]; then
	if [[ -f KPOINTS ]]; then
		ckpoint=0
	else
		ckpoint=1
	fi
fi
if [[ "$ckpoint" -gt 0 ]]; then
	kpoint=$(awk '{print sqrt($1*$1+$2*$2+$3*$3)}' temp_x2p_lattice | awk '{printf"%d ",int(20/$1)+1}')
	echo -e "mesh auto\n0\nG\n$kpoint\n0 0 0" >KPOINTS
	if [ $gammamode == "no" ]; then
		echo -e "    Creat KPOINTS successfully ( $kpoint) !!!\n"
	else
		echo -e "    Creat KPOINTS successfully ( 1 1 1 ) !!!\n"
	fi
fi
# creat job.script
if [[ "$cscript" == -1 ]]; then
	if [[ -f $jobscript ]]; then
		cscript=1
	else
		cscript=0
	fi
fi
if [[ "$cscript" -gt 0 ]]; then
	if [[ ! -f sbatch.vasp ]]; then
		if [[ $lowmode != "no" ]]; then
			cp $examdir/sbatch.vasp_low ./sbatch.vasp
		else
			cp $examdir/sbatch.vasp ./sbatch.vasp
		fi
	fi
	USER=$(pwd | awk -F/ '{print $5}')
	sed -i 's/^#SBATCH -J .*/#SBATCH -J '"$USER-${xsdfile%.*}"'/g' sbatch.vasp
fi

# set U-value
if [[ "$setpU" == -1 ]]; then
	if [[ -f INCAR ]]; then
		setpU=1
	else
		setpU=0
	fi
fi
if [[ "$setpU" -gt 0 ]]; then
	if [[ ! -f INCAR ]]; then
		cp $examdir/INCAR .
	fi
	if [[ -d "$pUdir" ]]; then
		for i in $(awk '{print $1}' temp_x2p_shortinfo); do
			if [[ ! -f "$pUdir/$i" ]]; then
				plusUerror=1
				missU=$missU" "$i
			fi
		done
		if [[ "$plusUerror" == 1 ]]; then
			echo -e "    The DFT+U parameters of ($missU ) is nonexistent,\n    DFT+U set cancel! You can try \"xsd2pos -h\" for help!"
		else
			for i in $(awk '{printf"%s \n",$1}' temp_x2p_shortinfo); do
				if [[ -f "$workdir/$i" ]]; then
					cat $workdir/$i | awk -F \# '{print $1}' | xargs >>temp_x2p_Uvalue
				else
					cat $pUdir/$i | awk -F \# '{print $1}' | xargs >>temp_x2p_Uvalue
				fi
			done
			sed -i 's/LDAUL *=.*/LDAUL ='"$(cat temp_x2p_Uvalue | awk '{printf"    %2s  ",$1}')"'/' INCAR
			sed -i 's/LDAUU *=.*/LDAUU ='"$(cat temp_x2p_Uvalue | awk '{printf" %7.4f",$2}')"'/' INCAR
			sed -i 's/LDAUJ *=.*/LDAUJ ='"$(cat temp_x2p_Uvalue | awk '{printf" %7.4f",$3}')"'/' INCAR
			echo -e "    The U parameters updated!!!\n"
		fi
	fi
fi

echo -e "  <<<<<<<<<<<<<<<<<<<<<<<<<<<=>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
rm -f temp_x2p_*

if [ $gammamode != "no" ]; then
	before="EXEC=/public1/home/sc81049/soft/vasp/bin/vasp_std"
	after="EXEC=/public1/home/sc81049/soft/vasp/bin/vasp_gam"
	sed -i "s#$before#$after#" sbatch.vasp
	sed -i "4c\1 1 1" KPOINTS
fi

if [ $inmode == "NEB" ]; then
	rm POSCAR
	#	read -p "Please input IMAGES,node,ppn: " IMAGES node ppn
	EXEC="EXEC=/public1/home/sc81049/soft/vasp+vtst/bin/vasp_gam"
	sed -i "/EXEC=/c$EXEC" sbatch.vasp
	#sed -i "s/nodes=1/nodes=$node/" vasp.script
	#sed -i "s/ppn=20/ppn=$ppn/" vasp.script
	sed -i "s/LCLIMB = .TRUE./LCLIMB = .FALSE./" INCAR
	sed -i "s/EDIFFG = -0.05/EDIFFG = -0.1/" INCAR
	sed -i "s/IOPT = 1/IOPT = 3/" INCAR
	sed -i "s/IMAGES = 4/IMAGES = $IMAGES/" INCAR
	sed -i "4c\1 1 1" KPOINTS
	echo -e "\e[1;31m <EDIFFG = -0.1>\n<LCLIMB = .FALSE.> \n <IOPT = 3> \n\e[0m"
	echo -e "\e[1;31m Please don't forget check NPAR and IMAGES!!!\n \e[0m"
	echo -e "\e[1;31m KPOINTS set to Gamma point!\n \e[0m"
fi

if [ $inmode == "CINEB" ]; then
	rm POSCAR
	#	read -p "Please input IMAGES,node,ppn: " IMAGES node ppn
	before="EXEC=/data/apps/vasp/5.4.1/vasp"
	after="EXEC=/data/apps/vasp/5.4.1/old/vtst+TS/vasp_gam"
	#sed -i "s#$before#$after#" vasp.script
	#sed -i "s/nodes=1/nodes=$node/" vasp.script
	#sed -i "s/ppn=20/ppn=$ppn/" vasp.script
	sed -i "s/IMAGES = 4/IMAGES = $IMAGES/" INCAR
	sed -i "4c\1 1 1" KPOINTS
	echo -e "\e[1;31m <LCLIMB = .TRUE.> \n <IOPT = 1> \n\e[0m"
	echo -e "\e[1;31m Please don't forget check NPAR and IMAGES!!!\n \e[0m"
	echo -e "\e[1;31m KPOINTS set to Gamma point!\n \e[0m"
fi

if [ $inmode == "dimer" ]; then
	before="EXEC=/data/apps/vasp/5.4.1/vasp"
	after="EXEC=/data/apps/vasp/5.4.1/old/vasp"
	#sed -i "s#$before#$after#" vasp.script
fi

# MD set
if [ $inmode == "MD" ]; then
	echo -e "\e[1;31m POTIM set to 0.5(fs)!\n \e[0m"
	echo -e "\e[1;31m Please don't forget check TEBEG and TEEND!!!\n \e[0m"
fi

# chg_cal
if [ $inmode == "chg" ]; then
	before="#PBS -l walltime=72:00:00"
	after="#PBS -l walltime=24:00:00"
	#sed -i "s/$before/$after/" vasp.script
fi

# dos_cal
if [ $inmode == "DOS" ]; then
	before="#PBS -l walltime=72:00:00"
	after="#PBS -l walltime=12:00:00"
	#sed -i "s/$before/$after/" vasp.script
fi

# freq_cal
if [ $inmode == "freq" ]; then
	before="#PBS -l walltime=72:00:00"
	after="#PBS -l walltime=18:00:00"
	#sed -i "s/$before/$after/" vasp.script
fi

# nelect_set
if [ $nelectmode != "no" ]; then
	ele_num_str=$(sed -n '7p' POSCAR)
	#OLD_IFS="$IFS"
	#IFS=" "
	ele_num=($ele_num_str)
	#IFS=$OLD_IFS
	pattern=$(sed -n '1p' POTCAR | awk '{print $1}')
	eletron_str=$(egrep -A 1 "^\s+${pattern}" POTCAR | grep -v "-" | grep -v "$pattern")
	eletron=($eletron_str)
	sum_eletron=0
	for i in ${!ele_num[@]}; do
		sum_ele=$(echo "${ele_num[i]}*${eletron[i]}" | bc)
		sum_eletron=$(echo "${sum_eletron}+${sum_ele}" | bc)
	done
	symbol=$(echo $nelectmode | cut -c 2)
	value=$(echo $nelectmode | cut -c 3-)
	nelect=$(echo ${sum_eletron%.*}${symbol}${value} | bc)
	sed -i "/ALGO/c\  ALGO = All" INCAR
	sed -i "/ALGO/a\  NELECT = ${nelect}" INCAR
	echo -e "\e[1;31m NELECT = ${nelect} \e[0m \n"
fi

# sol_set
if [ $solmode != "no" ]; then
	sed -i "/LSOL/d" INCAR
	sed -i "/LREAL/a\  LSOL = .TRUE." INCAR
	echo -e "\e[1;31m Solvation effect considering!\e[0m \n"
fi

# VDW set
if [ $vdwmode != "no" ]; then
	sed -i "/IVDW/d" INCAR
	sed -i "/ENCUT/a\  IVDW = 12" INCAR
	echo -e "\e[1;31m VDW interaction included!\e[0m \n"
fi

# Low accuracy
if [ $lowmode != "no" ]; then
	sed -i "/ENCUT/c\  ENCUT = 300" INCAR
	echo -e "\e[1;31m Low accuracy prefered!\e[0m \n"
fi

# hse set
if [ $hsemode != "no" ]; then
	sed -i "/LHFCALC/,/PRECFOCK/ d" INCAR
	sed -i "/GGA/a\  LHFCALC = .TRUE.\n  HFSCREEN = 0.2\n  TIME = 0.4\n  PRECFOCK = Fast" INCAR
	sed -i "/LDAU/,/LMAXMIX/ d" INCAR
	echo -e "\e[1;31m HSE functional applied!\e[0m \n"
fi

# LMAXMIX set
lmaxmix=$(grep LDAUL INCAR | grep 3 | wc -l)
if [ $lmaxmix -ne 0 ]; then
	sed -i "/LMAXMIX/c\  LMAXMIX = 6" INCAR
else
	sed -i "/LMAXMIX/c\  LMAXMIX = 4" INCAR
fi
