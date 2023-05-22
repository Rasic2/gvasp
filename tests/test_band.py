import pytest

from gvasp.common.file import EIGENVAL


class TestBand(object):

    def test_band_write(self):
        EIGENVAL("EIGENVAL").write()


if __name__ == '__main__':
    pytest.main([__file__])
