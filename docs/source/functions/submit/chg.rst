Charge Density
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Charge Density calculation is another important task, you can also use :program:`QVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command:

.. code-block:: bash

    QVasp submit chg

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    QVasp submit chg -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.