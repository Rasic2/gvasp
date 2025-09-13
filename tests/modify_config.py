import json
from pathlib import Path

config = {'potdir': f"{Path('.').absolute()}/tests/pot"}

with open(f"{Path('.').absolute()}/gvasp/config.json", 'w') as f:
    json.dump(config, f)
