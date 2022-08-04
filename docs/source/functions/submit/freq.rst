Frequency
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Frequency calculation is often used to check imaginary frequency, IR spectrum modelling, free energy correction and so on.

Likewise the :ref:`optimization <optimization>` task, you can also use :program:`QVasp` to handle its inputs, just run the command:

.. code-block:: bash

    QVasp submit freq

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    QVasp submit freq -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.