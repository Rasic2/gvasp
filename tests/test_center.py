import os
from pathlib import Path

import pytest

from gvasp.common.plot import PostDOS
from gvasp.common.setting import RootDir

selector = {
    "atoms": "Pt",
    "orbitals": "d",
    "xlim": [-15, 0]
}


def change_dir(func):
    def wrapper(self, *args, **kargs):
        os.chdir(f"{Path(RootDir).parent}/tests/plot_center")
        func(self, *args, **kargs)
        os.chdir("../")

    return wrapper


class TestCenter(object):

    @change_dir
    def test_center(self):
        poster = PostDOS(dos_files=["DOSCAR"], pos_files=["CONTCAR"], LORBIT=10)
        poster.center(selector)


if __name__ == '__main__':
    pytest.main([__file__])
