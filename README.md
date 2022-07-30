## QVasp

A quick post-process for resolve or assistant the VASP calculations, `still in development`.

## Directory

* [Lib](Lib) (store the *.pyd files)

* [scripts](scripts) (scripts to resolve some not often encountered problems)

* [VaspTask](VaspTask) (mainly to create the `INCAR`, `POSCAR`, `POTCAR`, `KPOINTS` and `job.script` from
  only `*.xsd` file)

* [tests](tests) (test files for `QVasp`)

* [Temp](Temp) (some temp scripts, mostly of them are useless)

## Notes

Mostly scripts can be run in a single *.py or *.sh file, but still some process need first to be compiled, for
example, [**chgcar2grd**](ChargeDensity/grd/chgcar2grd).

Therefore, if you want to use them, you may compile them by yourself. Of course, I also
provide [Makefile](ChargeDensity/grd/Makefile) to help the compilation.

For example, you can compile the chgcar2grd like this:

```
cd ChargeDensity/grd;
make;
```

or

```
g++ -g -O3 chgcar2grd -c chgcar2grd.cpp
```

While for the `*.pyx` file, operation above may not work, you need to write the `setup.py` firstly, and then run the
following command:

- MACOS/Linux System
    ```
    python setup.py build_ext --inplace
    ```
  and the `*.so` file can be created and imported by the python.


- Windows System
    ```
    1. Run "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" in CMD
    2. python.exe setup.py build_ext --inplace --compiler=msvc
    ```
  and thr `*.pyd` file can be created and imported by the python.

## Requirements

* GNU compiler (gcc, gfortran and g++)
* MSVC compiler
* Python >= 3.9
* Cython
* matplotlib
* numpy == 1.23.1
* pymatgen == 2022.7.25
* pymatgen-diffusion == 2020.10.8




