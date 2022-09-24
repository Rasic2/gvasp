import inspect
import json
import os
import re
import shutil
from pathlib import Path

from gvasp.common.encoder import PathJSONEncoder
from gvasp.common.utils import get_HOME

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
        self.scheduler = None

        self.load()

    def __repr__(self):
        return f"------------------------------------Configure Information--------------------------------- \n" \
               f"! ConfigDir:      {self.config_dir} \n" \
               f"! INCAR-template: {self.template} \n" \
               f"! UValue:         {self.UValue} \n" \
               f"! scheduler:      {self.scheduler.stem} \n" \
               f"! PotDir:         {self.potdir} \n" \
               f"! LogDir:         {self.logdir} \n" \
               f"------------------------------------------------------------------------------------------"

    def load(self):
        """
        Load the configuration (need consider the multi-users)
        """
        # check config.json, if not exist, `config set to {}`
        try:
            with open(f"{RootDir}/config.json", "r") as f:
                config = json.load(f)
        except NotADirectoryError:
            config = {}

        # check config_dir, if not specify this key, set to RootDir
        try:
            self.config_dir = Path(config['config_dir'])  # config directory
        except KeyError:
            self.config_dir = Path(RootDir)

        # specify the INCAR && UValue.yaml template
        self.template = self.config_dir / 'INCAR'  # location of template
        self.UValue = self.config_dir / 'UValue.yaml'  # location of UValue

        # record the potdir and the path is not checked here
        if 'potdir' in config and config['potdir'] is not None:
            string = config['potdir']
            env_matches = re.findall(r"[/\\]*\$(\w+)[/\\]*", string)
            for match in env_matches:
                if os.getenv(match):
                    string = string.replace("$" + match, os.getenv(match))  # may cause bug, e.g. $HOME && $HOMEPATH
            self.potdir = Path(string).expanduser()
        else:
            self.potdir = None

        # specify the logdir, if not exist, set to HomeDir/logs
        try:
            if Path(config['logdir']).exists():
                self.logdir = Path(config['logdir'])  # location of logdir
            else:
                self.logdir = HomeDir / "logs"
        except KeyError:
            self.logdir = HomeDir / "logs"

        # specify the scheduler
        self.scheduler = config.get("scheduler", "slurm")

    def __setattr__(self, key, value):
        if key == "scheduler" and self.config_dir is not None:
            scheduler_path = self.config_dir / f'{value}.submit'
            if not scheduler_path.exists():
                raise ValueError(f"{value}.submit is not exist, please check")
            else:
                self.__dict__[key] = scheduler_path
        else:
            self.__dict__[key] = value

    @property
    def dict(self):
        return {'config_dir': self.config_dir, 'INCAR': self.template, 'potdir': self.potdir, 'logdir': self.logdir,
                'UValue': self.UValue, 'scheduler': self.scheduler.stem}

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


if __name__ == '__main__':
    config = ConfigManager()
    print()
