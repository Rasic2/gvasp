Density of States
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Density of States (DOS) calculation is another important task, you can also use :program:`GVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command:

.. code-block:: bash

    gvasp submit dos

.. attention::
    This command only generate the **INCAR**, **KPOINTS**, **POSCAR** and **POTCAR** files, thus you should prepare other files (e.g. CHGCAR) by yourself.

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    gvasp submit dos -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.

apply sequential task
----------------------

If you finally want to perform the DOS calculation, we recommend you use the following command:

.. code-block:: bash

    gvasp submit dos -s/--sequential

and the task will perform the optimization, charge calculation and DOS calculation in a sequential task.

.. note::
    Sequential task also support the :ref:`low <low>` and :ref:`analysis <analysis>` options.