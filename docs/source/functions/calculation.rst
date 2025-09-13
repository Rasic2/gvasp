Calculation Utils
========================

This section summary various calculation utils, including the surface energy calculation (0), electrostatic interaction energy calculation (1) and thermo-correction (2), while the usage of :code:`task 1` can see `here <https://pubs.acs.org/doi/10.1021/acscatal.1c04856>`_. Different tasks are specified by the command number.

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

Thermo-correction
---------------------

You can use :program:`GVasp` perform the thermo-correction by the following command:

.. code-block:: bash

    gvasp calc 2 -t temperature

where the :code:`temperature` represents the temperature you want to consider, default is 298.15 K.
