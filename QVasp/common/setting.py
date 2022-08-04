import inspect
import json
import os
import platform
from pathlib import Path

Version = "0.0.1"
Platform = platform.platform()

ComDir = os.path.dirname(os.path.abspath(os.path.realpath(inspect.getfile(inspect.currentframe()))))
RootDir = os.path.dirname(ComDir)
WorkDir = Path.cwd()


class ConfigManager(object):

    def __init__(self):
        self.config_dir = None
        self.template = None
        self.potdir = None
        self.logdir = None
        self.UValue = None

    def __repr__(self):
        return f"------------------------------------Configure Information--------------------------------- \n" \
               f"! ConfigDir:      {self.config_dir} \n" \
               f"! INCAR-template: {self.template} \n" \
               f"! UValue:         {self.UValue} \n" \
               f"! PotDir:         {self.potdir} \n" \
               f"! LogDir:         {self.logdir} \n" \
               f"------------------------------------------------------------------------------------------"

    def load(self):
        with open(f"{RootDir}/config.json", "r") as f:  # TODO: can modify
            config = json.load(f)

        try:
            self.config_dir = Path(config['config_dir'])  # config directory
        except KeyError:
            self.config_dir = Path(RootDir)

        self.template = self.config_dir / 'INCAR'  # location of template
        self.potdir = self.config_dir / 'pot'  # location of potdir
        self.UValue = self.config_dir / 'UValue.yaml'  # location of UValue

        if Path(config['logdir']).exists():
            self.logdir = Path(config['logdir'])  # location of logdir
        else:
            self.logdir = Path(RootDir) / "logs"

        return self

    @property
    def dict(self):
        return {'config_dir': self.config_dir, 'INCAR': self.template, 'potdir': self.potdir, 'logdir': self.logdir,
                'UValue': self.UValue}

    def write(self):
        with open(f"{RootDir}/config.json", "w") as f:
            json.dump(self.dict, f)

        return self.load()


Config = ConfigManager().load()
