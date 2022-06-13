#!/bin/bash

# To check the input file for VASP
# Contributed by Gang Tang, Linjie Chen, and so on

if [ -e INCAR ]&&[ -e POSCAR ]&&[ -e POTCAR ]; then #文件是否存在
  if [ -e KPOINTS ]; then
    echo ""
    echo -e "\033[33m Input Files are ok. \033[0m"
    echo ""
    echo -e "\033[33m KPOINTS: \033[0m"
    varkpo=$(tail -3 KPOINTS)
    echo -e "\033[33m $varkpo \033[0m"
    echo ""
  else
    kspacing=$(grep -o "KSPACING" INCAR | cut -d '=' -f1 | tr -d "\r\n") #grep -o 只打印匹配到的字符 cut -d 指定分隔符 -f 指定第几个字段 tr -d 删除
    if [ "$kspacing"x == "KSPACING"x ]; then
      echo ""
      echo -e "\033[33m Input Files are ok. \033[0m"
      varinc=$(grep "KSPACING" INCAR)
      echo ""
      echo -e "\033[33m $varinc \033[0m"
      echo ""
    else
      echo -e "\033[33m $(grep "KSPACING" INCAR) \033[0m"
      echo -e "\033[33m KPOINTS or KSPACING do not exit! \033[0m"
      echo ""
    fi
  fi

  FromPOT=$(grep -o "VRHFIN =[a-zA-Z]\+" POTCAR | cut -d '=' -f2 | tr 'a-z' 'A-Z');
  FromPOS=$(head -6 POSCAR | tail -1 | grep -o "[a-zA-Z]\+" | tr 'a-z' 'A-Z');
  if [[ ${FromPOT} == ${FromPOS} ]]; then
    varatom=$(sed -n '6p' POSCAR | tr -d "\r\n") #sed 只打印第6行
    echo -e "\033[33m Elsments are the same ($varatom) in POSCAR and POTCAR. \033[0m"
  else
    echo "Check failed " "Elements in POTCAR are:"
    echo ${FromPOT}
    echo "while elements in POSCAR are:"
    echo ${FromPOS}
  fi

  echo ""
  echo -e "\033[33m Atoms Number are $(sed 7'q;d' POSCAR | awk '{sum=0; for (i=1; i<=NF; i++) { sum+= $i } print sum}') \033[0m"
  echo ""

else
  if [ -e POSCAR ]; then
    echo " "
    echo -e "\033[33m POSCAR: \033[0m"
    varpos=$(sed -n '6,8p' POSCAR)
    echo -e "\033[33m $varpos \033[0m"
    echo -e "\033[33m Atoms Number are $(sed 7'q;d' POSCAR | awk '{sum=0; for (i=1; i<=NF; i++) { sum+= $i } print sum}') \033[0m"
    echo " "
  else
    echo -e "\033[33m POSCAR do not exit! \033[0m"
    echo " "
  fi

  if [ ! -e INCAR ]; then
    echo -e "\033[33m INCAR do not exit! \033[0m"
    echo " "
  fi

  if [ ! -e POTCAR ]; then
    echo -e "\033[33m POTCAR do not exit! \033[0m"
    echo " "
  fi

  if [ ! -e KPOINTS ]; then
    echo -e "\033[33m KPOINTS do not exit! \033[0m"
    echo " "
  fi
fi

