import inspect
import json
import os
from pathlib import Path

import yaml



ComDir = os.path.dirname(os.path.abspath(os.path.realpath(inspect.getfile(inspect.currentframe()))))
RootDir = os.path.dirname(ComDir)

with open(f"{RootDir}/config.json", "r") as f:  # TODO: can modify
    CONFIG = json.load(f)

WorkDir = Path.cwd()
ConfigDir = Path(CONFIG['config_dir'])  # directory of some necessary files (e.g., INCAR, pot, UValue.yaml)
INCARTemplate = ConfigDir / CONFIG['INCAR']  # location of incar_template
PotDir = ConfigDir / CONFIG['potdir']  # location of potdir
LogDir = ConfigDir / CONFIG['logdir']

with open(ConfigDir / CONFIG['UValue']) as f:
    UValue = yaml.safe_load(f.read())