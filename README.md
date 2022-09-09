# GVasp Manual

![GitHub](https://img.shields.io/github/license/Rasic2/gvasp)
[![Documentation Status](https://readthedocs.org/projects/qvasp/badge/?version=latest)](https://qvasp.readthedocs.io/en/latest/?badge=latest)
[![Anaconda-Server Badge](https://anaconda.org/hui_zhou/gvasp/badges/installer/conda.svg)](https://conda.anaconda.org/hui_zhou)
[![Anaconda-Server Badge](https://anaconda.org/hui_zhou/gvasp/badges/platforms.svg)](https://anaconda.org/hui_zhou/gvasp)
![Codecov](https://img.shields.io/codecov/c/github/Rasic2/gvasp)

## Table of contents

- [About GVasp](#about-gvasp)
- [Install](#install)
    - [Create Environment](#create-environment)
    - [Install GVasp](#install-gvasp)
- [Setting Environment](#setting-environment)
    - [Default Environment](#default-environment)
    - [Modify Environment](#modify-environment)
- [Code Structure](#code-structure)
- [Requirements](#requirements)

## About GVasp

A quick post-process for resolve or assistant the VASP calculations, which can involve in many kinds of tasks as below:

* generate inputs
* visualize output
* visualize trajectory
* plot interface
* charge related work

More detailed information can see [here](https://qvasp.readthedocs.io/en/latest/).

## Install

### Create Environment

Before install the `GVasp`, we strongly recommend you to install [conda](https://www.anaconda.com/products/distribution)
before.

After install conda, create a new environment, e.g. `gvasp`, and install a `python (version=3.9)`, using following
command:

```
conda create -n gvasp python=3.9
```

### Install GVasp

1. From sourcecode

   You can install the `GVasp` using the following command (under the root directory):

    ```
    python3 setup.py install
    ```

   or

    ```
    pip3 install .
    ```
2. Use PyPi

   We have made the wheel (production process can
   see [here](https://qvasp.readthedocs.io/en/latest/package.html#pypi-wheel)) and upload to
   the [pypi](https://pypi.org/project/gvasp/),
   you can also install from it:

    ```
    pip3 install gvasp
    ```
   If the download speed is too slow, we suggest you change the pip mirror by modifying the `~/.pip/pip.conf` file.

3. Use conda

   We now also made a conda package (production process can
   see [here](https://qvasp.readthedocs.io/en/latest/package.html#conda-package)) and uploaded to
   the [Anaconda](https://anaconda.org/hui_zhou/gvasp), so you can also install `GVasp` from it:

    ```
    conda install -c hui_zhou gvasp
    ```

If you run the `gvasp -v` and print version information, then you install the `GVasp` successful ~~

```
GVasp version 0.0.3 (Linux-5.10.16.3-microsoft-standard-WSL2-x86_64-with-glibc2.35)
```

## Setting Environment

### Default Environment

Default environment can display by following command:

```
gvasp -l/--list
```

Initial environment is like this:

```
------------------------------------Configure Information---------------------------------
! ConfigDir:      /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp
! INCAR-template: /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/INCAR
! UValue:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/UValue.yaml
! scheduler:      slurm
! PotDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/pot
! LogDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/logs
------------------------------------------------------------------------------------------
```

- ConfigDir: represents the directory of `INCAR (template)`, `UValue.yaml` and `pot`

- scheduler: represents the job control system, now only support slurm (but you can specify a .submit file in your parent-chain path)

- LogDir: represents the directory of `logs`

- INCAR: `INCAR template` file for all `GVasp` submit tasks

- UValue.yaml: define the `UValue` for elements

- pot: directory of the elements' `POTCAR` (please prepare it by yourself)

The structure of `pot` like this:

```
pot
├── PAW_LDA
├── PAW_PBE
├── PAW_PW91
├── USPP_LDA
├── USPP_PW91
└── vdw_kernel.bindat
```

### Modify Environment

If you don’t like the [default environment](#default-environment), you can modify the environment by
writing a `config.json` (or other name, but `json` format), the structure
of `config.json` like this:

```
{
  "config_dir": "/your_directory_to_three_mentioned_files",
  "potdir": "/your_pot_directory",
  "logdir": "/your_logs_directory"
}
```

and run command:

```
gvasp config -f config.json
```

Then the environment will be reset, `GVasp` will auto search the `INCAR`and `UValue.yaml` under the `config_dir`.

### User template

`GVasp` support user to define their incar or submit template with the following steps:

1. Named the incar or submit template as the `*.incar` and `*.submit` files.

2. Put them in your parent directory or parent’s parent directory and so on (defined as the parent-chain).

After these two steps, the GVasp generate the inputs will apply your templates.

## Code Structure

* [gvasp](gvasp): source code directory

* [gvasp/common](gvasp/common): main module

* [gvasp/neb](gvasp/neb): neb-related path module

* [gvasp/lib](gvasp/lib): store the dynamic library (*.so and *.pyd)

* [extension](extension): `C++`/`Cython` extensions (source code)

* [docs](docs): documents file (*.rst format)

* [tests](tests): test files

## Requirements

* Python >= 3.9
* Cython
* pybind11
* numpy
* matplotlib

Copyright © 2022 `Hui Zhou` All rights reserved.

