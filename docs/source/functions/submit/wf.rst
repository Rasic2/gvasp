Work Function
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Work Function (WF) calculation is another important task, you can also use :program:`GVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command:

.. code-block:: bash

    gvasp submit wf

From finished job
--------------------

Meantime, you can also start a wf task from a finished job which has the CONTCAR file, and the :program:`GVasp` will auto generate the inputs for this task, just run the following command:

.. code-block:: bash

    gvasp submit wf -C/--continuous

.. note::
    This feature is also support for the chg and dos tasks.

apply sequential task
----------------------

If you finally want to perform the WF calculation, we recommend you use the following command:

.. code-block:: bash

    gvasp submit wf -s/--sequential

and the task will perform the optimization and WF calculation in a sequential task.

.. note::
    Sequential task also support the :ref:`low <low>` option.

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.
