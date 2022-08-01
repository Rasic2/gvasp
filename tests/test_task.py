from common.task import OptTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, DimerTask


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


def dimer():
    task = DimerTask()
    task.generate()


if __name__ == '__main__':
    dimer()
