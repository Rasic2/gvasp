import inspect
import json
import os
import platform
import shutil
from pathlib import Path

from gvasp.common.encoder import PathJSONEncoder
from gvasp.common.utils import get_HOME

Version = "0.0.1"
Platform = platform.platform()

ComDir = os.path.dirname(os.path.abspath(os.path.realpath(inspect.getfile(inspect.currentframe()))))
RootDir = os.path.dirname(ComDir)
WorkDir = Path.cwd()
HomeDir = get_HOME()


class ConfigManager(object):

    def __init__(self):
        self.config_dir = None
        self.template = None
        self.potdir = None
        self.logdir = None
        self.UValue = None

        self.load()

    def __repr__(self):
        return f"------------------------------------Configure Information--------------------------------- \n" \
               f"! ConfigDir:      {self.config_dir} \n" \
               f"! INCAR-template: {self.template} \n" \
               f"! UValue:         {self.UValue} \n" \
               f"! PotDir:         {self.potdir} \n" \
               f"! LogDir:         {self.logdir} \n" \
               f"------------------------------------------------------------------------------------------"

    def load(self):
        try:
            with open(f"{RootDir}/config.json", "r") as f:
                config = json.load(f)
        except NotADirectoryError:
            config = {}

        try:
            self.config_dir = Path(config['config_dir'])  # config directory
        except KeyError:
            self.config_dir = Path(RootDir)

        self.template = self.config_dir / 'INCAR'  # location of template
        self.UValue = self.config_dir / 'UValue.yaml'  # location of UValue
        self.potdir = Path(config['potdir']) if 'potdir' in config and config['potdir'] is not None else None

        try:
            if Path(config['logdir']).exists():
                self.logdir = Path(config['logdir'])  # location of logdir
            else:
                self.logdir = HomeDir / "logs"
        except KeyError:
            self.logdir = HomeDir / "logs"

    @property
    def dict(self):
        return {'config_dir': self.config_dir, 'INCAR': self.template, 'potdir': self.potdir, 'logdir': self.logdir,
                'UValue': self.UValue}

    def write(self):
        shutil.copyfile(f"{RootDir}/config.json", f"{RootDir}/config_ori.json")
        try:
            with open(f"{RootDir}/config.json", "w") as f:  # dangerous, write to a temp file and substitute the origin
                json.dump(self.dict, f, cls=PathJSONEncoder, indent=2)
        except Exception as error:
            shutil.copyfile(f"{RootDir}/config_ori.json", f"{RootDir}/config.json")
            print("Warning: error happen, use original environment setting")
            raise error
        else:
            print("Successfully update the config.json")
