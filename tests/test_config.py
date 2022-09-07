import json
import unittest
from pathlib import Path

from common.encoder import PathJSONEncoder
from common.setting import ConfigManager


class TestConfig(unittest.TestCase):
    def test_config(self):
        config = ConfigManager()
        config.write()


if __name__ == '__main__':
    unittest.main()
