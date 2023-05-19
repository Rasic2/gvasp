import os
import unittest
from pathlib import Path

from gvasp.common.setting import RootDir
from gvasp.common.task import OptTask, FreqTask, NEBTask


def file_cleaner(func):
    def wrapper(self, *args, **kargs):
        func(self, *args, **kargs)
        for file in Path(".").glob("*.arc"):
            os.remove(file)

    return wrapper


class TestMovie(unittest.TestCase):
    @file_cleaner
    def test_opt(self):
        OptTask.movie()

    @file_cleaner
    def test_freq(self):
        os.chdir(f"{Path(RootDir).parent}/tests/freq")
        FreqTask.movie(freq=0)
        os.chdir("../")


if __name__ == '__main__':
    unittest.main()
