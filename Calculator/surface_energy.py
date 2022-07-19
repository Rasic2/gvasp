#!/usr/bin/env python

def surf(E_slab,n,E_unit,A):
	gamma=(E_slab-n*E_unit)/(2*A)*16
	return gamma

#lattice=-98.44304124
lattice=-97.96633971
E_unit=lattice/4
CeO2_100=-332.58964702
CeO2_100_Ot=-381.92470187
A=7.70746**2

surf1=surf(CeO2_100,14,E_unit,A)
surf2=surf(CeO2_100_Ot,16,E_unit,A)
print(surf1,"\t",surf2)
