import pytest

from gvasp.common.plot import PlotPES, PlotCCD


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


if __name__ == '__main__':
    pytest.main([__file__])
