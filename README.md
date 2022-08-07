# GVasp Manual

![GitHub](https://img.shields.io/github/license/Rasic2/gvasp)
[![Documentation Status](https://readthedocs.org/projects/qvasp/badge/?version=latest)](https://qvasp.readthedocs.io/en/latest/?badge=latest)
[![Anaconda-Server Badge](https://anaconda.org/hui_zhou/qvasp/badges/installer/conda.svg)](https://conda.anaconda.org/hui_zhou)

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

A quick post-process for resolve or assistant the VASP calculations, which can involve in four kinds of tasks as below:

* generate inputs
* visualize trajectory
* plot interface
* charge related work

More detailed information can see [here](https://qvasp.readthedocs.io/en/latest/).

## Install

### Create Environment

Before install the `GVasp`, we strongly recommend you to install [conda](https://anaconda.org/) before.

After install conda, create a new environment, e.g. `GVasp`, and install a `python (version=3.9)`, using following
command:

```
conda create -n GVasp python=3.9
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

   We have made the wheel (production process can see [here]) and upload to the [pypi](https://pypi.org/project/gvasp/),
   you can also install from it:

    ```
    pip3 install gvasp
    ```
   If the download speed is too slow, we suggest you change the pip mirror by modifying the `~/.pip/pip.conf` file.

3. Use conda

   We now also made a conda package (production process can see [here]) and uploaded to
   the [Anaconda](https://anaconda.org/hui_zhou/gvasp), so you can also install `GVasp` from it:

    ```
    conda install -c hui_zhou -c conda-forge gvasp
    ```

If you run the `gvasp -v` and print version information, then you install the `GVasp` successful ~~

```
GVasp version 0.0.1 (Linux-5.10.16.3-microsoft-standard-WSL2-x86_64-with-glibc2.35)
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
! PotDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/pot
! LogDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/logs
------------------------------------------------------------------------------------------
```

- ConfigDir: represents the directory of `INCAR (template)`, `UValue.yaml` and `pot`

- LogDir: represents the directory of `logs`

- INCAR: `INCAR template` file of all `GVasp` submit tasks

- UValue.yaml: define the `UValue` for elements

- pot: directory of the elements' `POTCAR`

The structure of pot is like this:

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
writing a `config.json`, the format
of config.json is like this:

```
{
  "config_dir": "/your_directory_to_three_mentioned_files",
  "logdir": "/your_logs_directory",
}
```

and run command:

```
gvasp config -f config.json
```

Then the environment will be reset, `GVasp` will auto search the `INCAR`, `UValue.yaml`, `pot` under the `config_dir`.

## Code Structure

* [gvasp](gvasp) source code directory of `GVasp`
   gvasp
* [gvasp/common](gvasp/common) (main module of `GVasp`)
   gvasp
* [gvasp/lib](gvasp/lib) (store the *.pyd files)

* [extension](extension) (`C++`/`Cython` extensions for `GVasp`)

* [docs](docs) (document description)

* [tests](tests) (test files of `GVasp`)

## Requirements

* Python >= 3.9
* Cython
* matplotlib
* numpy == 1.23.1 (other version may conflict with pymatgen, not test)
* pymatgen == 2022.7.25
* pymatgen-diffusion == 2020.10.8
