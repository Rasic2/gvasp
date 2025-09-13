Dimer Method
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

`Dimer <http://theory.cm.utexas.edu/vtsttools/dimer.html>`_ is also a method to locate the TS, which allows the user to start from any initial configuration and search for a nearby saddle point, but actually it not very often use relative to :ref:`Con-TS <con-TS>` and :ref:`NEB <neb_topic>` methods.

:program:`GVasp` also support the Dimer method to locate the TS, just run the command below:

.. code-block:: bash

    gvasp submit dimer

.. attention::
    The Dimer method is not very useful, so **GVasp** provide a little support to this method. We also recommend user to try :ref:`Con-TS <con-TS>` or :ref:`NEB <neb_topic>` method to locate the TS.

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.
