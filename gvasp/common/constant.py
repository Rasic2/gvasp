import platform
import time

Version = "0.1.2"
Platform = platform.platform()
DATE = time.strftime("%Y-%m-%d", time.localtime())

BLACK = "\033[1;30m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
BOLD = "\033[1m"
RESET = "\033[0m"

ORBITALS = ['s', 'p', 'd', 'f']
COLUMNS_8 = ['s_up', 's_down', 'p_up', 'p_down', 'd_up', 'd_down', 'f_up', 'f_down']
COLUMNS_32 = ['s_up', 's_down', 'py_up', 'py_down', 'pz_up', 'pz_down', 'px_up', 'px_down', 'dxy_up', 'dxy_down',
              'dyz_up', 'dyz_down', 'dz2_up', 'dz2_down', 'dxz_up', 'dxz_down', 'dx2_up', 'dx2_down', 'f1_up',
              'f1_down', 'f2_up', 'f2_down', 'f3_up', 'f3_down', 'f4_up', 'f4_down', 'f5_up', 'f5_down', 'f6_up',
              'f6_down', 'f7_up', 'f7_down']
