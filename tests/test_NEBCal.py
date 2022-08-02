from common.task import NEBTask

task = NEBTask(ini_poscar="POSCAR_IS_sort", fni_poscar="POSCAR_FS_sort", images=4)
task.generate(method="liner")
print()