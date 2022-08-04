Plot Interface
=================================

:program:`QVasp` support optimization, band structure, density of states, potential energy surface as well as the neb images plot. Each plot task can use :code:`--save` or :code:`--show` to save or show the output figure. For the plot setting and data load, one need to use :code:`-j/--json` to specify one json file to handle it.

.. note::
    **-\-save** and **-\-show** can't as the arguments at the meantime.

Detailed arguments setting can see the **sub-topics** below.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   plot/opt
   plot/band
   plot/dos
   plot/pes
   plot/neb

.. note::
    We recommend user plot the figure under the **Win/MAC OS** system, because **Linux** may lack some necessary fonts.