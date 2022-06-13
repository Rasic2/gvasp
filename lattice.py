#!/usr/bin/env python
# -*- coding: utf-8 -*-
#####################################################################
# File Name: lattice.py
# Author: wdhu@59.78.92.45
# Created Time: Sat 10 May 2014 06:27:09 PM CST
#####################################################################
import numpy as np
#import commands
import os
from sys import argv

if len(argv) != 2:
	infile = "POSCAR"
else:
	infile = argv[1]

os.environ['infile']=str(infile)
#Ax = float(commands.getoutput("x=`cat $infile | sed -n '3p' | awk '{print $1}'`;echo $x"))
#Ay = float(commands.getoutput("y=`cat $infile | sed -n '3p' | awk '{print $2}'`;echo $y"))
#Az = float(commands.getoutput("z=`cat $infile | sed -n '3p' | awk '{print $3}'`;echo $z"))
Ax = float(os.popen("x=`cat $infile | sed -n '3p' | awk '{print $1}'`;echo $x").read().rstrip())
Ay = float(os.popen("y=`cat $infile | sed -n '3p' | awk '{print $2}'`;echo $y").read().rstrip())
Az = float(os.popen("z=`cat $infile | sed -n '3p' | awk '{print $3}'`;echo $z").read().rstrip())
A = ((Ax**2)+(Ay**2)+(Az**2))**(1.0/2.0)
#Bx = float(commands.getoutput("x=`cat $infile | sed -n '4p' | awk '{print $1}'`;echo $x"))
#By = float(commands.getoutput("y=`cat $infile | sed -n '4p' | awk '{print $2}'`;echo $y"))
#Bz = float(commands.getoutput("z=`cat $infile | sed -n '4p' | awk '{print $3}'`;echo $z"))
Bx = float(os.popen("x=`cat $infile | sed -n '4p' | awk '{print $1}'`;echo $x").read().rstrip())
By = float(os.popen("y=`cat $infile | sed -n '4p' | awk '{print $2}'`;echo $y").read().rstrip())
Bz = float(os.popen("z=`cat $infile | sed -n '4p' | awk '{print $3}'`;echo $z").read().rstrip())
B = ((Bx**2)+(By**2)+(Bz**2))**(1.0/2.0)
#Cx = float(commands.getoutput("x=`cat $infile | sed -n '5p' | awk '{print $1}'`;echo $x"))
#Cy = float(commands.getoutput("y=`cat $infile | sed -n '5p' | awk '{print $2}'`;echo $y"))
#Cz = float(commands.getoutput("z=`cat $infile | sed -n '5p' | awk '{print $3}'`;echo $z"))
#C = ((Cx**2)+(Cy**2)+(Cz**2))**(1.0/2.0)
Cx = float(os.popen("x=`cat $infile | sed -n '5p' | awk '{print $1}'`;echo $x").read().rstrip())
Cy = float(os.popen("y=`cat $infile | sed -n '5p' | awk '{print $2}'`;echo $y").read().rstrip())
Cz = float(os.popen("z=`cat $infile | sed -n '5p' | awk '{print $3}'`;echo $z").read().rstrip())
C = ((Cx**2)+(Cy**2)+(Cz**2))**(1.0/2.0)
alpla = np.arccos((Bx*Cx+By*Cy+Bz*Cz)/(B*C))*180/np.pi
beta = np.arccos((Ax*Cx+Ay*Cy+Az*Cz)/(A*C))*180/np.pi
gamma = np.arccos((Bx*Ax+By*Ay+Bz*Az)/(B*A))*180/np.pi
vol = np.array([[Ax,Ay,Az],[Bx,By,Bz],[Cx,Cy,Cz]])
#
print(infile)
print("     a is   %12.8f"% A)
print("     b is   %12.8f"% B)
print("     c is   %12.8f"% C)
print(" alpla is   %10.6f"% alpla)
print("  beta is   %10.6f"% beta)
print(" gamma is   %10.6f"% gamma)
print("volume is %12.6f"% np.linalg.det(vol))
