Density of States
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Density of States (DOS) calculation is another important task, you can also use :program:`QVasp` to handle its inputs.

Likewise the :ref:`optimization <optimization>` task, run the command:

.. code-block:: bash

    QVasp submit dos

.. attention::
    This command only generate the **INCAR**, **KPOINTS**, **POSCAR** and **POTCAR** files, thus you should prepare other files (e.g. CHGCAR) by yourself.

specify potential
-------------------

If you want to specify potential, just run the command:

.. code-block:: bash

    QVasp submit dos -p/--potential POTENTIAL

.. note::
    More information of potential setting can be seen in :ref:`optimization <potential>` task.