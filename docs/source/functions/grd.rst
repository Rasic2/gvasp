Generate Grd File
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

:file:`*.grd` can be load by `Material Studio <https://www.3ds.com/products-services/biovia/products/molecular-modeling-simulation/biovia-materials-studio/>`_, so :program:`GVasp` provide the transform from :file:`CHGCAR_mag` to it.

The command is:

.. code-block:: bash

    gvasp grd [-n/--name NAME] [-d/--DenCut DENCUT]

* name parameter specify the output name of \*.grd, default is :file:`vasp.grd`.

* DenCut parameter specify the cutoff density (set it can decrease the size of grd file), default is 250.