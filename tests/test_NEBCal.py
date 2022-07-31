from common.task import NEBCal

task = NEBCal(ini_POSCAR="POSCAR_IS_sort", fni_POSCAR="POSCAR_FS_sort", images=4)
task.generate(method="liner")
print()