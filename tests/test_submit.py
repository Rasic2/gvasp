import os
import shutil
import sys
import unittest

from QVasp.common.task import OptTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, DimerTask, NEBTask


def file_cleaner(func):
    def wrapper(self, *args, **kargs):
        func(self, *args, **kargs)
        os.remove("INCAR")
        os.remove("KPOINTS")
        os.remove("POTCAR")

    return wrapper


def block_print(func):
    def wrapper(self, *args, **kwargs):
        sys.stdout = open(os.devnull, 'w')
        func(self, *args, **kwargs)
        sys.stdout.close()
        sys.stdout = sys.__stdout__

    return wrapper


class TestSubmitTask(unittest.TestCase):

    @block_print
    @file_cleaner
    def test_opt(self):
        task = OptTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_chg(self):
        task = ChargeTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_dos(self):
        task = DOSTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_freq(self):
        task = FreqTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_md(self):
        task = MDTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_stm(self):
        task = STMTask()
        task.generate()

    @block_print
    @file_cleaner
    def test_neb(self):
        task = NEBTask(ini_poscar="POSCAR_IS_sort", fni_poscar="POSCAR_FS_sort", images=4)
        task.generate(method="linear")

        for dir in NEBTask._search_neb_dir():
            shutil.rmtree(dir)

    @block_print
    @file_cleaner
    def test_dimer(self):
        task = DimerTask()
        task.generate()


if __name__ == '__main__':
    unittest.main()
