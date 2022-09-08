import shutil
import unittest
from pathlib import Path

from gvasp.common.file import XSDFile


class TestOutput(unittest.TestCase):
    def test_output(self):
        XSDFile.write(contcar=Path(".") / "tests" / "CONTCAR", outcar=Path(".") / "tests" / "OUTCAR")
        shutil.rmtree("output.xsd")


if __name__ == '__main__':
    unittest.main()
