import pytest

from gvasp.common.task import OptTask


@pytest.fixture()
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class TestSubmitMag:

    def test_opt_mag(self, change_test_dir):
        task = OptTask()
        task.generate(vdw=True, sol=True, mag=True, low=True)


if __name__ == '__main__':
    pytest.main([__file__])
