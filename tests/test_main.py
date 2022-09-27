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

    def test_submit(self):
        args = ["opt", "chg", "wf", "dos", "freq", "md", "con-TS", "stm", "dimer"]

        for arg in args:
            main(["submit"] + [arg])


if __name__ == '__main__':
    pytest.main([__file__])
