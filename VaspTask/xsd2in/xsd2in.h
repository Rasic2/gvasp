#!/usr/bin/bash

cpot=1
cscript=1
ckpoint=1
setmag=1
setpU=1
incell=0
potmode=ori
cmark=_c
sortZ=1 #>0:sort by atoms Z axis; 0: only sort by atom element name.

workdir=$(pwd)
potcfgdir=$HOME
jobscript=sbatch.vasp
potdir=/mnt/c/Users/hui_zhou/Desktop/VASP_scripts/VaspTask/xsd2in/pot/PAW_PBE
examdir=/mnt/c/Users/hui_zhou/Desktop/VASP_scripts/VaspTask/xsd2in/example/PBE
pUdir=/mnt/c/Users/hui_zhou/Desktop/VASP_scripts/VaspTask/xsd2in/Uvalue
VaspEXEC=/mnt/c/Users/hui_zhou/Desktop/VASP_scripts/VaspTask/xsd2in/vasp_std
VaspNebEXEC=/mnt/c/Users/hui_zhou/Desktop/VASP_scripts/VaspTask/xsd2in/vasp_std

inmode=opt
gammode=no
solmode=no
hsemode=no
vdwmode=no
lowmode=no
nelectmode=no

IMAGES=4
ppn=20
node=1