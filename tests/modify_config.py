import json
from pathlib import Path

from gvasp.common.setting import RootDir

config = {"potdir": f"{Path(RootDir).parent}/tests/pot"}

with open(f"{Path(RootDir)}/config.json", "w") as f:
    json.dump(config, f)
