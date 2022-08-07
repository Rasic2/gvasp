import json
from pathlib import Path

from common.encoder import PathJSONEncoder
from common.setting import ConfigManager

config = ConfigManager()
config.write()

print()
