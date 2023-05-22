import os
from pathlib import Path

import pytest

from gvasp.common.calculator import electrostatic_energy
from gvasp.common.setting import RootDir


def change_dir(func):
    def wrapper(self, *args, **kargs):
        os.chdir(f"{Path(RootDir).parent}/tests/electrostatic")
        func(self, *args, **kargs)
        os.chdir("../")

    return wrapper


class TestElectrostatic(object):

    @change_dir
    def test_electrostatic(self):
        electrostatic_energy(atoms=["Ce"])


if __name__ == '__main__':
    pytest.main([__file__])
