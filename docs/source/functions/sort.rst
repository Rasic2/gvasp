.. _align:

Align Structures
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

If you use the :program:`GVasp` to generate the :ref:`NEB <neb_topic>` inputs, the first thing is align the structure, because the atoms in initial and final structures may not one-to-one.

The command is simple, like this:

.. code-block:: bash

    gvasp sort --ini_poscar INI_POSCAR --fni_poscar FNI_POSCAR

.. note::
    The INI_POSCAR and FNI_POSCAR are names provided by user of the initial and final structures.

Then :program:`GVasp` will generate two POSCAR files which suffix is :file:`_sort`.

.. note::
    To check if the align success, you can visualize the NEB (set the :code:`-p/-\-pos=POSCAR`), detailed information can see :ref:`here <neb_movie>`.