#!/usr/bin/env python
# -*- coding: utf-8 -*-
#####################################################################
# File Name: lattice.py
# Author: wdhu@59.78.92.45
# Created Time: Sat 10 May 2014 06:27:09 PM CST
#####################################################################
import numpy as np
import os

Ax = float(os.popen("sed -n 3'p' POSCAR | awk '{print $1}'").read().rstrip())
Ay = float(os.popen("sed -n 3'p' POSCAR | awk '{print $2}'").read().rstrip())
Az = float(os.popen("sed -n 3'p' POSCAR | awk '{print $3}'").read().rstrip())
A = ((Ax**2)+(Ay**2)+(Az**2))**(1.0/2.0)
Bx = float(os.popen("sed -n '4p' POSCAR | awk '{print $1}'").read().rstrip())
By = float(os.popen("sed -n '4p' POSCAR | awk '{print $2}'").read().rstrip())
Bz = float(os.popen("sed -n '4p' POSCAR | awk '{print $3}'").read().rstrip())
B = ((Bx**2)+(By**2)+(Bz**2))**(1.0/2.0)
Cx = float(os.popen("sed -n '5p' POSCAR | awk '{print $1}'").read().rstrip())
Cy = float(os.popen("sed -n '5p' POSCAR | awk '{print $2}'").read().rstrip())
Cz = float(os.popen("sed -n '5p' POSCAR | awk '{print $3}'").read().rstrip())
C = ((Cx**2)+(Cy**2)+(Cz**2))**(1.0/2.0)
alpla = np.arccos((Bx*Cx+By*Cy+Bz*Cz)/(B*C))*180/np.pi
beta = np.arccos((Ax*Cx+Ay*Cy+Az*Cz)/(A*C))*180/np.pi
gamma = np.arccos((Bx*Ax+By*Ay+Bz*Az)/(B*A))*180/np.pi
vol = np.array([[Ax,Ay,Az],[Bx,By,Bz],[Cx,Cy,Cz]])

print("POSCAR")
print("     a is   %12.8f"% A)
print("     b is   %12.8f"% B)
print("     c is   %12.8f"% C)
print(" alpla is   %10.6f"% alpla)
print("  beta is   %10.6f"% beta)
print(" gamma is   %10.6f"% gamma)
print("volume is %12.6f"% np.linalg.det(vol))
