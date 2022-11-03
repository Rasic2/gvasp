Install
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

You can install the **GVasp** use the conda and pip tools, or compile it from the source code in GitHub.

Conda install
--------------

.. code-block:: bash

    conda install gvasp -c hui_zhou -c conda-forge

.. note::
    If you have trouble in installation, you can add the --force-reinstall to force reinstall the GVasp.

Pip install
-------------

.. code-block:: bash

    pip install gvasp

Source code compilation
------------------------

.. code-block:: bash

    python setup.py install

or

.. code-block:: bash

    pip install .

If you run the :code:`gvasp -v` and print version information, then you install the :program:`GVasp` successful ~~

.. code-block:: bash

    GVasp version x.x.x (Linux-5.10.16.3-microsoft-standard-WSL2-x86_64-with-glibc2.35)

