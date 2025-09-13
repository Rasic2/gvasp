Visualize Trajectory
=================================

Visualize is a useful method to check calculation process, :program:`GVasp` provide visualize support for various VASP tasks, i.e., optimization, moleculer dynamics, frequency, and TS search.

The idea is to transform the :file:`XDATCAR` (for :ref:`optimization <opt_movie>`, :ref:`moleculer dynamics <md_movie>`, :ref:`frequency <freq_movie>`, :ref:`con-TS <con-TS_movie>`, and :ref:`dimer <dimer_movie>` tasks) or [:file:`POSCAR` | :file:`CONTCAR`] (for :ref:`neb <neb_movie>` task) to the :file:`*.arc` file (`Material Studio <https://www.3ds.com/products-services/biovia/products/molecular-modeling-simulation/biovia-materials-studio/>`_ accepted).

Except :ref:`frequency <freq_movie>`, other tasks accept optional [-n/-\-name] to specify the name of output :file:`*.arc`, other arguments will describe in corresponding sub-topic.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   movie/opt
   movie/md
   movie/freq
   movie/ts

.. note::
    More detailed information about the arc file display can see `here <https://codenote.readthedocs.io/en/latest/chemistry/MS.html#arc>`_.
