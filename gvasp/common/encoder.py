from json import JSONEncoder
from pathlib import Path


class PathJSONEncoder(JSONEncoder):
    """
    Extend the default JSONEncoder, make it accept the <Path> instance
    """

    def default(self, o):
        if isinstance(o, Path):
            return o.absolute().as_posix()
        else:
            return super().default(o)
