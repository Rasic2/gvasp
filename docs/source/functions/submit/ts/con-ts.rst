.. _con-TS:

Constrained-TS Method
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

`Constrained-TS (Con-TS) <https://pubs.acs.org/doi/10.1021/ja801648h>`_ is a much faster method to locate the transition state (TS), which searches for TSs from a guessed TS-like structure by fixing only one degree of freedom, e.g., the distance of the dissociating chemical bond.

:program:`GVasp` support to generate the inputs of Con-TS, just run the command below:

.. code-block:: bash

    gvasp submit con-TS

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.
