import logging
import os
import shutil
from pathlib import Path

import pytest

from gvasp.common.error import PotDirNotExistError, ParameterError, AnimationError, FrequencyError, \
    AttributeNotRegisteredError
from gvasp.common.file import EIGENVAL, OUTCAR, DOSCAR
from gvasp.common.file import MODECAR
from gvasp.common.file import MetaFile, XDATCAR, StructInfoFile, CellFile, POSCAR, SubmitFile, XSDFile, INCAR, POTCAR, \
    CHGBase, AECCAR0, AECCAR2
from gvasp.common.setting import RootDir
from tests.utils import change_dir

logger = logging.getLogger('TestLogger')


def setup_module():
    os.chdir(f'{Path(RootDir).parent}/tests')


class TestMetaFile:
    file = XDATCAR('XDATCAR')

    def test_new(self):
        with pytest.raises(TypeError):
            MetaFile('XDATCAR')

    def test_getitem(self):
        logger.info(self.file[0])

    def test_repr(self):
        logger.info(self.file)

    def test_type(self):
        logger.info(self.file.type)


class TestStructInfoFile:
    def test_new(self):
        with pytest.raises(TypeError):
            StructInfoFile('XDATCAR')


class TestCellFile:
    def test_to_POSCAR(self):
        cell_file = CellFile(name='CuO-HAc.cell')
        cell_file.to_POSCAR()


class TestPOSCAR:
    def test_dist(self):
        logger.info(POSCAR.dist('POSCAR_IS_sort', 'POSCAR_FS_sort'))


class TestSubmitFile:
    def test_build(self):
        name = 'temp_submit'
        with open(name, 'w') as f:
            f.write('# User-defined Pre-Process\n')
            f.write('a=1\n')
            f.write('# End Pre-Process\n')
            f.write('EXEC=/public1/home/sc81049/soft/vasp+vtst/bin/vasp_gam\n')
            f.write('# User-defined Post-Process\n')
            f.write('a=1\n')
            f.write('# End Post-Process\n')

        submit_file = SubmitFile(name=name).build
        os.remove(name)

        assert 'vasp_gam' in submit_file.vasp_gam_line


class TestXSDFile:

    def test_parse(self):
        XSDFile(name=Path(RootDir).parent / 'tests' / 'P1xsd' / 'Fe' / 'Fe.xsd')

    def test_write_relax(self):
        XSDFile.write(contcar=Path(RootDir).parent / 'tests' / 'CONTCAR',
                      outcar=Path(RootDir).parent / 'tests' / 'OUTCAR')
        os.remove('output-y.xsd')

    def test_write_fix(self):
        XSDFile.write(contcar=Path(RootDir).parent / 'tests' / 'CONTCAR_fix',
                      outcar=Path(RootDir).parent / 'tests' / 'OUTCAR')
        os.remove('output-y.xsd')


class TestINCAR:
    def test_getattr(self):
        incar = INCAR('INCAR_file')
        logger.info(f'PREC = {incar.PREC}')
        logger.info(f'prec = {incar.prec}')

    def test_init_attr(self):
        with open('INCAR_file', 'a') as f:
            f.write('  ERRORPARAM = None\n')

        with pytest.raises(AttributeNotRegisteredError):
            incar = INCAR('INCAR_file')

        with open('INCAR_file') as f:
            lines = [line for line in f.readlines() if 'ERRORPARAM' not in line]

        # 写回文件
        with open('INCAR_file', 'w') as f:
            f.writelines(lines)


class TestPOTCAR:
    def test_cat(self):
        pot_directory = Path(RootDir).parent / 'tests' / 'pot'

        with pytest.raises(PotDirNotExistError):
            POTCAR.cat(['PAW_PBE'], ['W'])

        with pytest.raises(TypeError):
            POTCAR.cat(['PAW'], ['W'], potdir=pot_directory)

        with pytest.raises(ParameterError):
            POTCAR.cat(['PAW_PBE'], [], potdir=pot_directory)

        POTCAR.cat(['PAW_PBE'], ['W'], potdir=pot_directory)


class TestCHGBase:
    def test_new(self):
        with pytest.raises(TypeError):
            CHGBase(name='AECCAR0')

    def test_add(self):
        aeccar0 = AECCAR0('AECCAR0')
        aeccar2 = AECCAR2('AECCAR2')

        aeccar0 = aeccar0.load()
        aeccar0 + aeccar2
        aeccar2.density = None
        aeccar2 + aeccar0


class TestEIGENVAL:
    def test_band_write(self):
        EIGENVAL('EIGENVAL').write()
        shutil.rmtree('band_data')


class TestOUTCAR:
    def test_animation_freq(self):
        with pytest.raises(AnimationError):
            outcar = OUTCAR('OUTCAR')
            outcar.animation_freq()

        with pytest.raises(FrequencyError):
            outcar = OUTCAR('freq/OUTCAR')
            outcar.animation_freq(freq=-1)

            outcar = OUTCAR('freq/OUTCAR')
            outcar.animation_freq(freq='i')

    def test_bandgap(self):
        OUTCAR('OUTCAR').bandgap()


class TestMODECAR:

    @change_dir(directory='freq')
    def test_from_freq(self):
        MODECAR.write_from_freq(freq=5, scale=0.6, outcar='OUTCAR')

    def test_from_POSCAR(self):
        MODECAR.write_from_POSCAR(f'{Path(RootDir).parent}/tests/POSCAR_IS_sort',
                                  f'{Path(RootDir).parent}/tests/POSCAR_FS_sort')


class TestDOSCAR:
    def test_init(self):
        with pytest.raises(SystemExit) as exit_info:
            doscar = DOSCAR('DOSCAR_dos', LORBIT=11)
        assert exit_info.value.code == 1
