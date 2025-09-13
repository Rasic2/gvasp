import logging
import shutil
from pathlib import Path

import pytest

from gvasp.common.setting import RootDir
from gvasp.common.task import OptTask, XDATMovie, NormalTask, ConTSTask, ChargeTask, WorkFuncTask, DOSTask, NEBTask
from tests.utils import change_dir

logger = logging.getLogger('TestLogger')


@pytest.fixture()
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class TestXDATMovie:
    def test_new(self):
        with pytest.raises(TypeError):
            XDATMovie()


class TestNormalTask:
    def test_new(self):
        with pytest.raises(TypeError):
            NormalTask()


class TestOptTask:

    @change_dir('continuous')
    def test_continuous(self, change_test_dir):
        task = OptTask()
        task.generate(continuous=True)

    @change_dir('continuous')
    def test_continuous_hse(self, change_test_dir):
        task = OptTask()
        task.generate(continuous=True, hse=True)

    def test_nelect(self):
        task = OptTask()
        task.generate(nelect=1)

    def test_static(self):
        task = OptTask()
        task.generate(static=True)


class TestConTSTask:

    @change_dir('continuous')
    def test_continuous(self, change_test_dir):
        task = ConTSTask()
        task.generate(continuous=True)


class TestChargeTask:

    @change_dir('continuous')
    def test_analysis(self, change_test_dir):
        task = ChargeTask()
        task.generate(continuous=True, analysis=True)


class TestWorkFuncTask:

    @change_dir('continuous')
    def test_continuous(self, change_test_dir):
        task = WorkFuncTask()
        task.generate(continuous=True)


class TestDOSTask:

    @change_dir('continuous')
    def test_continuous(self, change_test_dir):
        task = DOSTask()
        task.generate(continuous=True)


class TestNEBTask:

    @change_dir('neb')
    def test_monitor(self):
        NEBTask.monitor()


def teardown_module():
    try:
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'hse'}")
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'opt_cal'}")
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'ts_cal'}")
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'chg_cal'}")
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'dos_cal'}")
        shutil.rmtree(f"{Path(RootDir).parent / 'tests' / 'continuous' / 'workfunc'}")
        logger.info(f'Clean the Directory Success!')
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    pytest.main([__file__])
