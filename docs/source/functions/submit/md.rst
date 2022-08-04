Ab-initio Molecule Dynamics
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

For ab-initio molecule dynamics (AIMD), likewise the :ref:`optimization <optimization>` task, you can also use :program:`QVasp` to handle its inputs, just run the command:

.. code-block:: bash

    QVasp submit md

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    QVasp submit md -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.