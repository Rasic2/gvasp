import logging
import os
from pathlib import Path

import pytest

from gvasp.common.error import PotDirNotExistError, ParameterError
from gvasp.common.file import MetaFile, XDATCAR, StructInfoFile, CellFile, POSCAR, SubmitFile, XSDFile, INCAR, POTCAR
from gvasp.common.setting import RootDir

logger = logging.getLogger("TestLogger")


class TestMetaFile(object):
    file = XDATCAR("XDATCAR")

    def test_new(self):
        with pytest.raises(TypeError):
            MetaFile("XDATCAR")

    def test_getitem(self):
        logger.info(self.file[0])

    def test_repr(self):
        logger.info(self.file)

    def test_type(self):
        logger.info(self.file.type)


class TestStructInfoFile(object):
    def test_new(self):
        with pytest.raises(TypeError):
            StructInfoFile("XDATCAR")


class TestCellFile(object):
    def test_to_POSCAR(self):
        cell_file = CellFile(name="CuO-HAc.cell")
        cell_file.to_POSCAR()


class TestPOSCAR(object):
    def test_dist(self):
        logger.info(POSCAR.dist("POSCAR_IS_sort", "POSCAR_FS_sort"))


class TestSubmitFile(object):
    def test_build(self):
        name = "temp_submit"
        with open(name, "w") as f:
            f.write("EXEC=/public1/home/sc81049/soft/vasp+vtst/bin/vasp_gam\n")
        submit_file = SubmitFile(name=name).build
        os.remove(name)

        assert "vasp_gam" in submit_file.vasp_gam_line


class TestXSDFile(object):

    def test_parse(self):
        XSDFile(name=Path(RootDir).parent / "tests" / "P1xsd" / "Fe" / "Fe.xsd")

    def test_write_relax(self):
        XSDFile.write(contcar=Path(RootDir).parent / "tests" / "CONTCAR",
                      outcar=Path(RootDir).parent / "tests" / "OUTCAR")
        os.remove("output-y.xsd")

    def test_write_fix(self):
        XSDFile.write(contcar=Path(RootDir).parent / "tests" / "CONTCAR_fix",
                      outcar=Path(RootDir).parent / "tests" / "OUTCAR")
        os.remove("output-y.xsd")


class TestINCAR(object):
    def test_getattr(self):
        incar = INCAR("INCAR_file")
        logger.info(f"PREC = {incar.PREC}")


class TestPOTCAR(object):
    def test_cat(self):
        pot_directory = Path(RootDir).parent / "tests" / "pot"

        with pytest.raises(PotDirNotExistError):
            POTCAR.cat(["PAW_PBE"], ['W'])

        with pytest.raises(TypeError):
            POTCAR.cat(["PAW"], ["W"], potdir=pot_directory)

        with pytest.raises(ParameterError):
            POTCAR.cat(["PAW_PBE"], [], potdir=pot_directory)

        POTCAR.cat(["PAW_PBE"], ["W"], potdir=pot_directory)


if __name__ == '__main__':
    pytest.main([__file__, "--color=yes"])
