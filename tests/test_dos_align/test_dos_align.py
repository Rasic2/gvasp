import os

import pytest

from gvasp.common.plot import PostDOS


@pytest.fixture()
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class TestPlotDOS(object):

    def test_align(self, change_test_dir):
        selector = {"0": [{"atoms": 78, "orbitals": ["s"], "color": "#098760"}],
                    "1": [{"atoms": 81, "orbitals": ["s"], "color": "#ed0345"}]}

        dos_files = ["DOSCAR_N_doped_A_101_0e_Na", "DOSCAR_N_doped_A_101_0e_K"]
        pos_files = ["CONTCAR_N_doped_A_101_0e_Na", "CONTCAR_N_doped_A_101_0e_K"]
        poster = PostDOS(dos_files=dos_files, pos_files=pos_files, align=[(78, "s"), (81, "s")])
        poster.plot(selector=selector)
        poster.save()
        os.remove("figure.svg")


if __name__ == '__main__':
    pytest.main([__file__, "-s"])
