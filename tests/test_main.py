import pytest

from gvasp.main import main


class TestMain(object):
    def test_help(self):
        try:
            args = ["", "-h"]
            main(args)
        except SystemExit:
            pass

    def test_list(self):
        try:
            args = ["", "-l"]
            main(args)
        except SystemExit:
            pass

    def test_version(self):
        try:
            args = ["", "-v"]
            main(args)
        except SystemExit:
            pass


if __name__ == '__main__':
    pytest.main([__file__])
