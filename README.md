# QVasp Manual

![GitHub](https://img.shields.io/github/license/Rasic2/QVasp)
[![Documentation Status](https://readthedocs.org/projects/qvasp/badge/?version=latest)](https://qvasp.readthedocs.io/en/latest/?badge=latest)

## Table of contents

- [About QVasp](#about-qvasp)
- [Install](#install)
    - [Create Environment](#create-environment)
    - [Install QVasp](#install-qvasp)
- [Setting Environment](#setting-environment)
    - [Default Environment](#default-environment)
    - [Modify Environment](#modify-environment)
- [Code Structure](#code-structure)
- [Requirements](#requirements)

## About QVasp

A quick post-process for resolve or assistant the VASP calculations, which can involve in four kinds of tasks as below:

* generate inputs
* visualize trajectory
* plot interface
* charge related work

More detailed information can see [here](https://qvasp.readthedocs.io/en/latest/).

## Install

### Create Environment

Before install the `QVasp`, we strongly recommend you to install [conda](https://anaconda.org/) before.

After install conda, create a new environment, e.g. `QVasp`, and install a `python (version=3.9)`, using following
command:

```
conda create -n QVasp python=3.9
```

### Install QVasp

1. From sourcecode

   You can install the `QVasp` using the following command (under the root directory):

    ```
    python3 setup.py install
    ```

   or

    ```
    pip3 install .
    ```
2. Use PyPi

   We have made the wheel and upload to the [pypi](https://pypi.org/project/QVasp/), you can also install from it:

    ```
    pip3 install Qvasp
    ```
   If the download speed is too slow, we suggest you change the pip mirror by modifying the `~/.pip/pip.conf` file.

If you run the `QVasp -v` and print version information, then you install the `QVasp` successful ~~

```
QVasp version 0.0.1 (Linux-5.10.16.3-microsoft-standard-WSL2-x86_64-with-glibc2.35)
```

## Setting Environment

### Default Environment

Default environment can display by following command:

```
QVasp -l/--list
```

Initial environment is like this:

```
------------------------------------Configure Information---------------------------------
! ConfigDir:      /mnt/c/Users/hui_zhou/Desktop/packages/QVasp/QVasp
! INCAR-template: /mnt/c/Users/hui_zhou/Desktop/packages/QVasp/QVasp/INCAR
! UValue:         /mnt/c/Users/hui_zhou/Desktop/packages/QVasp/QVasp/UValue.yaml
! PotDir:         /mnt/c/Users/hui_zhou/Desktop/packages/QVasp/QVasp/pot
! LogDir:         /mnt/c/Users/hui_zhou/Desktop/packages/QVasp/QVasp/logs
------------------------------------------------------------------------------------------
```

- ConfigDir: represents the directory of `INCAR (template)`, `UValue.yaml` and `pot`

- LogDir: represents the directory of `logs`

- INCAR: `INCAR template` file of all `QVasp` submit tasks

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
QVasp config -f config.json
```

Then the environment will be reset, `QVasp` will auto search the `INCAR`, `UValue.yaml`, `pot` under the `config_dir`.

## Code Structure

* [QVasp](QVasp) source code directory of `QVasp`

* [QVasp/common](QVasp/common) (main module of `QVasp`)

* [QVasp/lib](QVasp/lib) (store the *.pyd files)

* [extension](extension) (`C++`/`Cython` extensions for `QVasp`)

* [docs](docs) (document description)

* [tests](tests) (test files of `QVasp`)

## Requirements

* Python >= 3.9
* Cython
* matplotlib
* numpy == 1.23.1 (other version may conflict with pymatgen, not test)
* pymatgen == 2022.7.25
* pymatgen-diffusion == 2020.10.8
