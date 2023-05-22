Electrostatic Potential Plot
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

For the electrostatic potential (ep), one can use :program:`GVasp` to plot it, just run the command:

.. code-block:: bash

    gvasp plot ep -j plot.json --save

then, one may obtain the :file:`figure.svg` which plot the electrostatic potential.

Just like this,

.. image:: ep.svg
   :align: center
   :width: 400

For this task, the :file:`plot.json` is like this

.. code-block:: json

    {
        "width": 5,
        "height": 4,
        "fontsize": 10
    }

The attention of :code:`--show`, :code:`--save` and :code:`--json` can be seen in :ref:`optimization <show_plot>` part.

