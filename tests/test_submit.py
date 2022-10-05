import os
import shutil
import sys
from pathlib import Path

import pytest

from gvasp.common.setting import RootDir
from gvasp.common.task import OptTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, DimerTask, NEBTask, \
    SequentialTask, ConTSTask, WorkFuncTask, BandTask


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


class TestSubmitTask(object):

    @block_print
    def test_opt(self):
        task = OptTask()
        task.generate(vdw=True, sol=True)

    @block_print
    def test_chg(self):
        task = ChargeTask()
        task.generate(vdw=True, sol=True, continuous=True)
        os.chdir("../")

    @block_print
    @file_cleaner
    def test_band(self):
        task = BandTask()
        task.generate(vdw=True, sol=True, continuous=True)
        os.chdir("../")

    @block_print
    @file_cleaner
    def test_wf(self):
        task = WorkFuncTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_dos(self):
        task = DOSTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_sequential(self):
        task = SequentialTask(end='dos')
        task.generate(low=True, analysis=True, vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_freq(self):
        task = FreqTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_md(self):
        task = MDTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_stm(self):
        task = STMTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_conTS(self):
        task = ConTSTask()
        task.generate(vdw=True, sol=True)

    @block_print
    @file_cleaner
    def test_neb(self):
        task = NEBTask(ini_poscar=f"{Path(RootDir).parent}/tests/POSCAR_IS_sort",
                       fni_poscar=f"{Path(RootDir).parent}/tests/POSCAR_FS_sort", images=4)
        task.generate(method="idpp", vdw=True, sol=True)

        for dir in NEBTask._search_neb_dir():
            shutil.rmtree(dir)

    @block_print
    @file_cleaner
    def test_dimer(self):
        task = DimerTask()
        task.generate(vdw=True, sol=True)


if __name__ == '__main__':
    pytest.main([__file__])
