import os
from pathlib import Path

import pytest

from gvasp.common.calculator import thermo_gas
from gvasp.common.setting import RootDir


def change_dir(func):
    def wrapper(self, *args, **kargs):
        os.chdir(f'{Path(RootDir).parent}/tests/entropy')
        func(self, *args, **kargs)
        os.chdir('../')

    return wrapper


class TestThermo(object):

    @change_dir
    def test_gas(self):
        thermo_gas(298.15)


if __name__ == '__main__':
    pytest.main([__file__])
