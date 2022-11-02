import os
import unittest
from pathlib import Path

from gvasp.common.file import XSDFile


class TestOutput(unittest.TestCase):
    def test_output(self):
        XSDFile.write(contcar=Path(".") / "tests" / "CONTCAR", outcar=Path(".") / "tests" / "OUTCAR")
        os.remove("output-y.xsd")


if __name__ == '__main__':
    unittest.main()
