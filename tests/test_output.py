import os
import unittest
from pathlib import Path

from gvasp.common.setting import RootDir
from gvasp.common.file import XSDFile


class TestOutput(unittest.TestCase):
    def test_output(self):
        XSDFile.write(contcar=Path(RootDir).parent / "tests" / "CONTCAR",
                      outcar=Path(RootDir).parent / "tests" / "OUTCAR")
        os.remove("output-y.xsd")


if __name__ == '__main__':
    unittest.main()
