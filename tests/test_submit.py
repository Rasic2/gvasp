import os
import shutil
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


class TestSubmitTask(object):

    def test_opt(self):
        task = OptTask()
        task.generate(vdw=True, sol=True)

    def test_opt_hse(self):
        task = OptTask()
        task.generate(hse=True)

    def test_chg(self):
        task = ChargeTask()
        task.generate(vdw=True, sol=True, continuous=True)
        os.chdir("../")
        shutil.rmtree("chg_cal")

    @file_cleaner
    def test_band(self):
        task = BandTask()
        task.generate(vdw=True, sol=True, continuous=True)
        os.chdir("../")
        shutil.rmtree("band_cal")

    @file_cleaner
    def test_wf(self):
        task = WorkFuncTask()
        task.generate(vdw=True, sol=True)

    @file_cleaner
    def test_dos(self):
        task = DOSTask()
        task.generate(vdw=True, sol=True)

    @file_cleaner
    def test_sequential_dos(self):
        task = SequentialTask(end='dos')
        task.generate(low=True, analysis=True, vdw=True, sol=True)

    @file_cleaner
    def test_sequential_wf(self):
        task = SequentialTask(end='wf')
        task.generate(low=True, analysis=True, vdw=True, sol=True)

    @file_cleaner
    def test_freq(self):
        task = FreqTask()
        task.generate(vdw=True, sol=True)

    @file_cleaner
    def test_md(self):
        task = MDTask()
        task.generate(vdw=True, sol=True)

    @file_cleaner
    def test_stm(self):
        task = STMTask()
        task.generate(vdw=True, sol=True)

    @file_cleaner
    def test_conTS(self):
        task = ConTSTask()
        task.generate(vdw=True, sol=True, low=True)

    @file_cleaner
    def test_neb_linear(self):
        task = NEBTask(ini_poscar=f"{Path(RootDir).parent}/tests/POSCAR_IS_sort",
                       fni_poscar=f"{Path(RootDir).parent}/tests/POSCAR_FS_sort", images=4)
        task.generate(method="linear", vdw=True, sol=True)

        for dir in NEBTask._search_neb_dir():
            shutil.rmtree(dir)

    @file_cleaner
    def test_neb_idpp(self):
        task = NEBTask(ini_poscar=f"{Path(RootDir).parent}/tests/POSCAR_IS_sort",
                       fni_poscar=f"{Path(RootDir).parent}/tests/POSCAR_FS_sort", images=4)
        task.generate(method="idpp", vdw=True, sol=True)

        for dir in NEBTask._search_neb_dir():
            shutil.rmtree(dir)

    @file_cleaner
    def test_dimer(self):
        task = DimerTask()
        task.generate(vdw=True, sol=True)


if __name__ == '__main__':
    pytest.main([__file__])
