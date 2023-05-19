import os
from functools import wraps
from pathlib import Path

from gvasp.common.setting import RootDir


def change_dir(directory):
    @wraps(directory)
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kargs):
            os.chdir(f"{Path(RootDir).parent}/tests/{directory}")
            func(self, *args, **kargs)
            os.chdir("../")

        return wrapper

    return inner
