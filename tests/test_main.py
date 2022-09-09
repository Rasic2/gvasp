import pytest

from gvasp.main import main_parser, main

parser = main_parser()


class TestMain():
    def test_help(self):
        try:
            args = parser.parse_args(["-h"])
            main(parser, args)
        except SystemExit:
            pass

    def test_list(self):
        args = parser.parse_args(["-l"])
        main(parser, args)

    def test_version(self):
        args = parser.parse_args(["-v"])
        main(parser, args)


if __name__ == '__main__':
    pytest.main(['./test_main.py'])
