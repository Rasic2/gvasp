import os

import pytest

from gvasp.common.plot import PlotPES
from gvasp.common.plot import PostDOS
from tests.utils import change_dir


@pytest.fixture()
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class TestPlot(object):

    # TODO: malloc error (see file.py [line 1082])
    # def test_CCD(self):
    #     plotter = PlotCCD()
    #     plotter.plot()
    #     plotter.save()

    def test_pes2(self):
        energy_1 = [0, -0.09, 0.75, 0.06, 0.26, -2.46, -1.02, -1.58]
        label_1 = ["MS", "MS", "TS", "MS", "TS", "MS", "TS", "MS"]

        energy_2 = [None, None, None, None, None, -2.46, -0.95, -1.66]
        label_2 = [None, None, None, None, None, "MS", "TS", "MS"]

        energy_3 = [0, None, None, 0.06, None, None, 0.39, -1.51]
        label_3 = ["MS", None, None, "MS", None, None, "TS", "MS"]

        plotter = PlotPES(width=8, height=6)
        plotter.plot(data=(energy_1, label_1), color="#000000", style="solid_curve")
        plotter.plot(data=(energy_2, label_2), color="#ed0345", style="solid_curve")
        plotter.plot(data=(energy_3, label_3), color="#A8F760", style="solid_curve")

        plotter.save()


class TestPlotDOS(object):
    selector = {"0": [{"atoms": 78, "orbitals": ["s"], "color": "#098760"}],
                "1": [{"atoms": 81, "orbitals": ["s"], "color": "#ed0345"}]}

    dos_files = ["DOSCAR_N_doped_A_101_0e_Na", "DOSCAR_N_doped_A_101_0e_K"]
    pos_files = ["CONTCAR_N_doped_A_101_0e_Na", "CONTCAR_N_doped_A_101_0e_K"]

    @change_dir("dos")
    def test_align(self, change_test_dir):
        poster = PostDOS(dos_files=self.dos_files, pos_files=self.pos_files, align=[(78, "s"), (81, "s")])
        poster.plot(selector=self.selector)
        poster.save()
        os.remove("figure.svg")

    @change_dir("dos")
    def test_align_error(self, change_test_dir):
        with pytest.raises(TypeError):
            poster = PostDOS(dos_files=self.dos_files, pos_files=self.pos_files, align=[(78,), (81, "s")])
            poster.plot(selector=self.selector)

    @change_dir("dos")
    def test_align_warning(self, change_test_dir):
        poster = PostDOS(dos_files=self.dos_files, pos_files=self.pos_files, align=[(81, "s")])
        poster.plot(selector=self.selector)

    @change_dir("dos")
    def test_method(self, change_test_dir):
        poster = PostDOS(dos_files=self.dos_files, pos_files=self.pos_files)

        selector = {"0": [{"atoms": 78, "orbitals": ["s"], "color": "#098760", "method": "dash line"}]}
        poster.plot(selector=selector)

        selector = {"0": [{"atoms": 78, "orbitals": ["s"], "color": "#098760", "method": "fill"}]}
        poster.plot(selector=selector)

        selector = {"0": [{"atoms": 78, "orbitals": ["s"], "color": "#098760", "method": "output"}]}
        poster.plot(selector=selector)
        os.remove("DOS_F0_L0")

    @change_dir("plot_center")
    def test_ispin(self, change_test_dir):
        selector = {"0": [{"atoms": "Pt", "orbitals": ["s"], "color": "#ed0345", "method": "line"}]}
        poster = PostDOS(dos_files=["DOSCAR_ispin"], pos_files=["CONTCAR_ispin"], ISPIN=1)
        poster.plot(selector=selector)

    @change_dir("plot_center")
    def test_center(self, change_test_dir):
        selector = {
            "atoms": "Pt",
            "orbitals": "d",
            "xlim": [-15, 0]
        }

        poster = PostDOS(dos_files=["DOSCAR"], pos_files=["CONTCAR"], LORBIT=10)
        poster.center(selector)

    @change_dir("plot_center")
    def test_center_atoms_None(self, change_test_dir):
        selector = {
            "orbitals": "d",
            "xlim": [-15, 0]
        }

        poster = PostDOS(dos_files=["DOSCAR"], pos_files=["CONTCAR"], LORBIT=10)
        poster.center(selector)

    @change_dir("plot_center")
    def test_center_orbitals_None(self, change_test_dir):
        selector = {
            "atoms": "Pt",
            "xlim": [-15, 0]
        }

        poster = PostDOS(dos_files=["DOSCAR"], pos_files=["CONTCAR"], LORBIT=10)
        poster.center(selector)

    @change_dir("plot_center")
    def test_center_ispin(self, change_test_dir):
        selector = {
            "ispin": 1,
            "atoms": "Pt",
            "xlim": [-15, 0]
        }

        poster = PostDOS(dos_files=["DOSCAR_ispin"], pos_files=["CONTCAR_ispin"], LORBIT=12)
        poster.center(selector)


if __name__ == '__main__':
    pytest.main([__file__, "-s"])
