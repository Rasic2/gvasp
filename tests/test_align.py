import os
import unittest
from pathlib import Path

from gvasp.common.file import POSCAR


class TestAlign(unittest.TestCase):
    def test_align(self):
        POSCAR.align("POSCAR_IS", "POSCAR_FS")
        for file in Path(".").glob("POSCAR_*_sort"):
            os.remove(file)


if __name__ == '__main__':
    unittest.main()
