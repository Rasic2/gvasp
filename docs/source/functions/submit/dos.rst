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

From finished job
--------------------

Meantime, you can also start a dos task from a finished job which has the CONTCAR and CHGCAR files, and the :program:`GVasp` will auto generate the inputs for this task, just run the following command:

.. code-block:: bash

    gvasp submit dos -C/--continuous

.. note::
    This feature is also support for the chg and wf tasks.

apply sequential task
----------------------

If you finally want to perform the DOS calculation, we recommend you use the following command:

.. code-block:: bash

    gvasp submit dos -s/--sequential

and the task will perform the optimization, charge calculation and DOS calculation in a sequential task.

.. note::
    Sequential task also support the :ref:`low <low>` and :ref:`analysis <analysis>` options.

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.
