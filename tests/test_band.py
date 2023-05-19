import shutil

import pytest

from gvasp.common.file import EIGENVAL, OUTCAR


class TestBand(object):

    def test_band_write(self):
        EIGENVAL("EIGENVAL").write()
        shutil.rmtree("band_data")

    def test_bandgap(self):
        OUTCAR("OUTCAR").bandgap()


if __name__ == '__main__':
    pytest.main([__file__])
