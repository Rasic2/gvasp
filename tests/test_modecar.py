from pathlib import Path

import pytest

from gvasp.common.file import MODECAR
from gvasp.common.setting import RootDir
from tests.utils import change_dir


class TestMODECAR:

    @change_dir(directory="freq")
    def test_from_freq(self):
        MODECAR.write_from_freq(freq=5, scale=0.6, outcar="OUTCAR")

    def test_from_POSCAR(self):
        MODECAR.write_from_POSCAR(f"{Path(RootDir).parent}/tests/POSCAR_IS_sort",
                                  f"{Path(RootDir).parent}/tests/POSCAR_FS_sort")


if __name__ == '__main__':
    pytest.main(["./test_modecar.py"])
