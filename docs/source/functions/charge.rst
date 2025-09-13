Charge Related
=================

This section solve the charge related tasks, such as chgsum, chgsplit and transform the CHGCAR to \*.grd file.

Charge Sum
------------

Charge Sum meaning sum to CHARGE file to CHGCAR_sum, i.e. :code:`AECCAR0 + AECCAR2 = CHGCAR_sum`.

The command is:

.. code-block:: bash

    gvasp sum

.. _split:

Charge Split
------------

Charge Split meaning split CHGCAR file to CHGCAR_tot and CHGCAR_mag, i.e. :code:`CHGCAR -> CHGCAR_tot + CHGCAR_mag`.

The command is:

.. code-block:: bash

    gvasp split

.. _grd:

Generate Grd File
-------------------

:file:`*.grd` can be load by `Material Studio <https://www.3ds.com/products-services/biovia/products/molecular-modeling-simulation/biovia-materials-studio/>`_, so :program:`GVasp` provide the transform from :file:`CHGCAR_mag` to it.

The command is:

.. code-block:: bash

    gvasp grd [-n/--name NAME] [-d/--DenCut DENCUT]

* name parameter specify the output name of \*.grd, default is :file:`vasp.grd`.

* DenCut parameter specify the cutoff density (set it can decrease the size of grd file), default is 250.

.. note::
    More detailed information about loading grd file in Material Studio can see `here <https://codenote.readthedocs.io/en/latest/chemistry/MS.html#grd>`_.
