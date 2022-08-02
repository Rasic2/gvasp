from common.task import OptTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, DimerTask, NEBTask


def optTask():
    task = OptTask()
    task.generate()


def chgTask():
    task = ChargeTask()
    task.generate()


def dos():
    task = DOSTask()
    task.generate()


def freq():
    task = FreqTask()
    task.generate()


def md():
    task = MDTask()
    task.generate()


def stm():
    task = STMTask()
    task.generate()


def neb():
    task = NEBTask(ini_POSCAR="POSCAR_IS_sort", fni_POSCAR="POSCAR_FS_sort", images=4)
    task.generate(method="linear")


def dimer():
    task = DimerTask()
    task.generate()


def freq_movie():
    FreqTask.movie()


if __name__ == '__main__':
    freq_movie()
