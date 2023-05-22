import os

import pytest

from gvasp.common.file import AECCAR0
from gvasp.common.task import ChargeTask


class TestCharge():

    def test_load(self):
        AECCAR0("AECCAR0").load()

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
    pytest.main(['./test_charge.py'])
