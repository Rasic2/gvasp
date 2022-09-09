import pytest

from gvasp.main import main_parser, main

parser = main_parser()


class TestMain():
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
    pytest.main(['./test_main.py'])
