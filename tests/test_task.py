import pytest

from gvasp.common.task import OptTask, XDATMovie, NormalTask
from tests.utils import change_dir


@pytest.fixture()
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class TestXDATMovie(object):
    def test_new(self):
        with pytest.raises(TypeError):
            XDATMovie()


class TestNormalTask(object):
    def test_new(self):
        with pytest.raises(TypeError):
            NormalTask()


class TestOptTask(object):

    @change_dir("continuous")
    def test_continuous(self, change_test_dir):
        task = OptTask()
        task.generate(continuous=True)

    def test_nelect(self):
        task = OptTask()
        task.generate(nelect=1)

    def test_static(self):
        task = OptTask()
        task.generate(static=True)


if __name__ == '__main__':
    pytest.main([__file__])
