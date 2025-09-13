Charge Density
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Charge Density calculation is another important task, you can also use :program:`GVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command (need a *.xsd file):

.. code-block:: bash

    gvasp submit chg

From finished job
--------------------

Meantime, you can also start a chg task from a finished job which has the CONTCAR file, and the :program:`GVasp` will auto generate the inputs for this task, just run the following command:

.. code-block:: bash

    gvasp submit chg -C/--continuous

.. note::
    This feature is also support for the wf and dos tasks.

.. _analysis:

open analysis option
---------------------

If you want to apply the `bader <http://theory.cm.utexas.edu/henkelman/code/bader/>`_ calculation, :ref:`chgsplit <split>` and :ref:`transform CHGCAR_mag to grd <grd>` after the charge calculation, you can run the following command:

.. code-block:: bash

    gvasp submit chg -a/--analysis

and the mentioned task will be performed in one task.

.. important::
    Make sure you add bader in your PATH environment.

apply sequential task
----------------------

If you finally want to perform the charge optimization, we recommend you use the following command:

.. code-block:: bash

    gvasp submit chg -s/--sequential

and the task will perform the optimization and charge calculation in a sequential task.

.. note::
    Sequential task also support the :ref:`low <low>` and :ref:`analysis <analysis>` options.

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.
