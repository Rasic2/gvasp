import os
import unittest

from common.task import ChargeTask


class TestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testcase):
        test_names = super().getTestCaseNames(testcase)
        test_methods = list(testcase.__dict__.keys())
        test_names = sorted(test_names, key=test_methods.index)
        return test_names


class TestCharge(unittest.TestCase):
    def test_sum(self):
        ChargeTask.sum()
        os.remove("CHGCAR_sum")

    def test_split(self):
        ChargeTask.split()
        os.remove("CHGCAR_tot")

    def test_grd(self):
        ChargeTask.to_grd()
        os.remove("CHGCAR_mag")
        os.remove("vasp.grd")


if __name__ == '__main__':
    unittest.main(testLoader=TestLoader())
