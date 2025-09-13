import os
from pathlib import Path

import matplotlib

matplotlibrc_path = Path(matplotlib.matplotlib_fname())
ttf_path = matplotlibrc_path.parent / 'fonts' / 'ttf'
Arial_path = Path('.').absolute() / 'tests' / 'Arial.ttf'
os.system(f'cp {Arial_path} {ttf_path}')
