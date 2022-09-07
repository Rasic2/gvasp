import unittest

from gvasp.common.setting import ConfigManager


class TestConfig(unittest.TestCase):
    def test_config(self):
        config = ConfigManager()
        config.write()


if __name__ == '__main__':
    unittest.main()
