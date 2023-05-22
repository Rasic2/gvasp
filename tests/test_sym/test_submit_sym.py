import os
from pathlib import Path

import pytest

from gvasp.common.setting import RootDir
from gvasp.common.task import SequentialTask


class TestSubmitSym(object):

    def test_sequential_sym(self):
        os.chdir(Path(RootDir).parent / "tests" / "test_sym")
        task = SequentialTask(end='chg')
        task.generate(vdw=True, sol=True)
        os.chdir("../")


if __name__ == '__main__':
    pytest.main([__file__])
