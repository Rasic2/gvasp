Package Production
===================

PyPi wheel
-----------

`PyPi <https://pypi.org/>`_ wheel is very simple to production, that you only need to write the correct :file:`setup.py`, and run the following command:

.. code-block:: bash

    python3 setup.py sdist bdist_wheel

then both :file:`*.tar.gz` and :file:`.whl` will occur at the :file:`./dist` directory.

It can be seen that, whether or not write the `correct` :file:`setup.py` will determine the success of the production, and :file:`setup.py` example can see below:

.. code-block:: python

    from distutils.extension import Extension
    from pathlib import Path

    from Cython.Build import cythonize
    from setuptools import setup, find_packages

    setup(
        name='gvasp',
        description='A quick post-process for resolve or assistant the VASP calculations',
        author='hui_zhou',
        long_description=Path("./README.md").read_text(),
        long_description_content_type='text/markdown',
        version='0.0.1',
        license='GPL-3.0',
        python_requires='>=3.9',
        packages=find_packages(),
        install_requires=[
            'Cython',
            'lxml',
            'matplotlib',
            'numpy',
            'pandas',
            'pymatgen',
            'pymatgen-analysis-diffusion',
            'pyyaml',
            'scipy'],
        ext_modules=cythonize([Extension(name='gvasp.lib._dos', sources=['extension/_dos/_dos.pyx']),
                               Extension(name='gvasp.lib._file', sources=['extension/_file/_file.cpp',
                                                                          'extension/_file/_lib.cpp'])], language_level=3),
        include_dirs=['/usr/lib/gcc/x86_64-linux-gnu/11/include', '/home/hzhou/anaconda3/include',
                      '/home/hzhou/anaconda3/Library/include'],
        include_package_data=True,
        package_data={"gvasp": ["*.json", "*.yaml", "INCAR", "pot.tgz"]},
        entry_points={'console_scripts': ['gvasp = gvasp.main:main']}
    )

where

    - *name*, *author*, *description*, *version* and *license* are package metadata

    - *long_description* are *long_description_content_type* are related description in `PyPi <https://pypi.org/>`_ (can write only once, before upload the package)

    - *packages* will search the module (including the :file:`__init__.py`) under **.** directory

    - *install_requires* is the dependency of the package, will installed when the package installed

    - *ext_modules* and *include_dirs* are related to the :code:`C/C++ extensions`

    - *package_data* is the data you want to including (which under the module); for other data (not in module), can write :file:`MANIFEST.in` to including them, like :download:`this <./MANIFEST.in>`

    - *entry_points* specify a alias **gvasp** to represent the :code:`python3 gvasp/main.py`

In fact, generate the :file:`*.whl` is the first step for :code:`Linux` platform, because `PyPi <https://pypi.org/>`_ will check the :code:`tag` of :file:`*.whl` file, only \*manylinux_* field in name can be accept according to `PEP rules <https://github.com/pypa/manylinux>`_ (:code:`PEP 513 (manylinux1)`, :code:`PEP 571 (manylinux2010)`, :code:`PEP 599 (manylinux2014)` and :code:`PEP 600 (manylinux_x_y)`). So one want to upload the package to PyPi should *repair* the wheel to have the `manylinux` field.

Luckily, by `docker image <https://github.com/pypa/manylinux>`_ and `auditwheel tool <https://pypi.python.org/pypi/auditwheel>`_, one can easily `repair` the `wheel`.

For example, following such steps:

1. pull the docker image, i.e., `manylinux_2_28_x86_64`

.. code-block:: bash

    docker pull quay.io/pypa/manylinux_2_28_x86_64

2. start and attach a container

.. code-block:: bash

    docker run -it quay.io/pypa/manylinux_2_28_x86_64 "/bin/bash"

3. transfer the source code to docker container

.. code-block:: bash

    docker cp local_path container_id:docker_path

4. recompile the package and obtain the \*.whl

.. code-block:: bash

    $python3 setup.py bdist_wheel

5. repair the \*.whl

.. code-block:: bash

    auditwheel repair *.whl

Finally, a new :file:`wheel` with the `manylinux` field will occur in the wheelhouse directory.

Then you can upload the `wheel` to `PyPi <https://pypi.org/>`_ use such command:

.. code-block:: bash

    twine upload dist/*

Conda package
--------------

Relative `PyPi <https://pypi.org/>`_ package production, production of conda package is very disgusting!!! Because you will meat the dependency problem every where.

Although, the conda package actually only need write :file:`meta.yaml` and :file:`build.sh` (at least for me), like this:

.. code-block:: yaml

    package:
      name: gvasp
      version: 0.0.1

    source:
      path: .

    requirements:
      build:
        - {{ compiler('c') }}
        - {{ compiler('cxx') }}

      host:
        - python
        - Cython
        - setuptools

      run:
        - python
        - numpy
        - Cython
        - lxml
        - matplotlib
        - pandas
        - pymatgen
        - pymatgen-analysis-diffusion
        - pyyaml
        - scipy

    about:
      home: https://github.com/Rasic2/gvasp
      license: GPL-3.0

and this:

.. code-block:: bash

    export CFLAGS="${CFLAGS} -isysroot ${CONDA_BUILD_SYSROOT}"
    export CXXFLAGS="${CXXFLAGS} -isysroot ${CONDA_BUILD_SYSROOT}"
    $PYTHON -m pip install . --no-deps -vv

Firstly, we talk about the :file:`meta.yaml`.

* `package` section represents the package information

* `source` section manage how to get the package (`git`, `pypi`, `local` or `other`), here we use `local` (we suggest that you mkdir a new directory (like :file:`conda`), and put the necessary source and data in there, including :file:`meta.yaml` and the :file:`bash.sh` below)

* `requirements` is very very disgusting, because they have three different part, i.e., :code:`build`, :code:`host`, :code:`run`.

    * :code:`build` represents the **system infrastructure**, so you can put `revision control systems (Git, SVN)`, `make tools (GNU make, Autotool, CMake)` and `compilers (real cross, pseudo-cross, or native when not cross-compiling)`, and `any source pre-processors` there. For example, we put :code:`C/C++ compilers` in this section.

    * :code:`host` is responsible for the :code:`setup.py`, in there, we use **Cython**, **setuptools** and inner module of **python**, so we put them in this section.

    * :code:`run` is simple, only equal to the `install_requires`, (noted that `pymatgen-\* packages` not in default channels, so we add the :code:`conda-forge` as the optional)

    * Actually, in the package production, conda will make a new directory under the `envs/**/conda-bld/package_name`. Under the directory, three directory will be made, i.e. :code:`_build_env`, :code:`_placeholder_placeholder_` and :code:`work`, where the compiler in :code:`build` section will download and installed in `_build_env`. The `_placeholder_placeholder_` directory manage the conda environment, for example, it will install the python, setuptools, Cython here, basically same to a new conda environment. The `work` dir is the copy of your source code, and the `real` build work will happen here, for example, :code:`compile` and :code:`package`.

Then we can talk about the :file:`build.sh`:

* Bacause of use Cython, we redefine of the :code:`CFLAGS` and :code:`CXXFLAGS`, detailed information can see `here <https://docs.conda.io/projects/conda-build/en/latest/resources/compiler-tools.html?highlight=Cython#macos-sdk>`_.

* env :code:`$PYTHON` represents the python version in `_placeholder_placeholder` directory, don't use the pure `python` command.

Here, we can use command below to process the real package production:

.. code-block:: bash

    conda-build . -c conda-forge

**.** represents the directory including the :file:`meta.yaml` and use the :code:`conda-forge` channel because of `pymatgen-*` packages.

After that, in :file:`conda-bld/linux-64` directory, the :file:`package.tar.bz2` has been written (`bin`, `info` and `lib` directory in it).

.. note::
    *bin* directory occur because we use **entry_points**; *info* directory store the **recipes** and **metadata**, *lib* is the real built package.

Finally, we can use :code:`Anaconda` command to upload the package:

.. code-block:: bash

    Anaconda upload *.tar.bz2

Install package can do this:

.. code-block:: bash

    conda install -c hui_zhou -c conda-forge qvasp

.. attention::
    When install the package, noticed that we used the compilers in **conda-forge** channel, so we particularly add this channel to install the package, otherwise conflicts will occur@@