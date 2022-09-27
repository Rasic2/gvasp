import pytest

from gvasp.main import main


class TestMain(object):
    def test_help(self):
        args = []
        main(args)

    def test_list(self):
        args = ["-l"]
        main(args)

    def test_version(self):
        args = ["-v"]
        main(args)


if __name__ == '__main__':
    pytest.main([__file__])
