Calculation Utils
========================

This section summary various calculation utils, including the surface energy calculation (0) and electrostatic interaction energy calculation (1), while the usage of the latter can see `here <https://pubs.acs.org/doi/10.1021/acscatal.1c04856>`_. Different tasks are specified by the command number.

surface energy calculation
----------------------------

You can use :program:`GVasp` calculate the surface energy by the following command:

.. code-block:: bash

    gvasp calc 0 -c crystal_dir -s slab_dir

where the :code:`crystal_dir` and :code:`slab_dir` represent the job directory for the crystal and slab models, respectively.

electrostatic interaction energy calculation
----------------------------------------------

You can use :program:`GVasp` calculate the electrostatic interaction energy by the following command:

.. code-block:: bash

    gvasp calc 1 -a atoms -w workdir

where the :code:`atoms` represents the atoms you want to calculate, and :code:`workdir` represents the work directory (default is ".") store the :file:`ACF.dat`.