Charge Density
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Charge Density calculation is another important task, you can also use :program:`GVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command:

.. code-block:: bash

    gvasp submit chg

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    gvasp submit chg -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.

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