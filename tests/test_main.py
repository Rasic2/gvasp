import os
import shutil
from pathlib import Path

import pytest

from gvasp.common.setting import RootDir
from gvasp.main import main
from tests.utils import change_dir


class TestMain(object):
    def test_help(self):
        main([])

        with pytest.raises(SystemExit):
            main(["-h"])

    def test_list(self):
        main(["-l"])

    def test_version(self):
        main(["-v"])

    def test_args_check(self):
        main(["submit", "chg", "-l"])

    def test_submit(self):
        args = ["opt", "chg", "wf", "dos", "freq", "md", "con-TS", "stm", "dimer"]

        for arg in args:
            main(["submit"] + [arg])

    def test_submit_sequential(self):
        args = ["chg", "wf", "dos"]

        for arg in args:
            main(["submit"] + [arg] + ["-s"])

    def test_submit_neb(self, monkeypatch):
        input_words = ['y', 'n']
        for word in input_words:
            with monkeypatch.context() as m:
                m.setattr('builtins.input', lambda prompt="": word)
                main(["submit", "neb", "-ini", f"{Path(RootDir).parent}/tests/POSCAR_IS_sort", "-fni",
                      f"{Path(RootDir).parent}/tests/POSCAR_FS_sort"])

        for directory in ["00", "01", "02", "03", "04", "05"]:
            shutil.rmtree(directory)

    def test_submit_neb_error(self, monkeypatch):
        with pytest.raises(AttributeError):
            main(["-d", "submit", "neb"])

    def test_output(self):
        main(["output"])
        os.remove("methane-y.xsd")

    def test_movie(self):

        @change_dir(directory="freq")
        def test_movie_freq(self):
            main(["movie", "freq"])

        @change_dir(directory="neb")
        def test_movie_neb(self):
            main(["movie", "neb"])

        main(["movie", "opt"])
        test_movie_freq(self)
        test_movie_neb(self)

    def test_sort(self):
        main(["sort", "-ini", f"{Path(RootDir).parent}/tests/POSCAR_IS", "-fni",
              f"{Path(RootDir).parent}/tests/POSCAR_FS"])

    def test_sort_error(self):
        with pytest.raises(AttributeError):
            main(["-d", "sort"])

    def test_plot(self):
        def test_plot_opt(self):
            main(["plot", "opt", "-j", "plot_opt.json", "--show"])

            main(["plot", "opt", "-j", "plot_opt.json", "--save"])

        def test_plot_ep(self):
            main(["plot", "ep", "-j", "plot_ep.json", "--save"])

        def test_plot_band(self):
            main(["plot", "band", "-j", "plot_band.json", "--save"])

        def test_plot_dos(self):
            main(["plot", "dos", "-j", "plot_dos.json", "--save"])

            with pytest.raises(TypeError):
                main(["-d", "plot", "dos", "-j", "plot_dos_error_dos_file.json", "--save"])

            with pytest.raises(AttributeError):
                main(["-d", "plot", "dos", "-j", "plot_dos_error_data.json", "--save"])

        def test_plot_pes(self):
            main(["plot", "PES", "-j", "plot_pes.json", "--save"])

        @change_dir(directory="neb")
        def test_plot_neb(self):
            main(["plot", "neb", "-j", "plot_neb.json", "--save"])
            os.remove("figure.svg")

        test_plot_opt(self)
        test_plot_ep(self)
        test_plot_band(self)
        test_plot_dos(self)
        test_plot_pes(self)
        test_plot_neb(self)

    @change_dir(directory="plot_center")
    def test_band_center(self):
        main(["band-center", "-j", "center.json"])

    def test_sum(self):
        main(["sum"])
        os.remove("CHGCAR_sum")

    def test_split(self):
        main(["split"])
        os.remove("CHGCAR_tot")

    def test_grd(self):
        main(["grd"])
        os.remove("CHGCAR_mag")
        os.remove("vasp.grd")

    @change_dir(directory="electrostatic")
    def test_electrostatic(self):
        main(['calc', "1", "-a", "Ce"])

    @change_dir(directory="entropy")
    def test_entropy(self):
        main(['calc', "2", "-t", "298.15"])


if __name__ == '__main__':
    pytest.main([__file__])
