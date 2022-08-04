Band Structure Plot
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

For the band structure, one can use :program:`QVasp` to plot it, just run the command:

.. code-block:: bash

    QVasp plot band -j plot.json --save

then, one may obtain the :file:`figure.svg` which plot the band structure.

Just like this,

.. image:: band.svg
   :align: center

For this task, the :file:`plot.json` is like this

.. code-block:: json

    {
        "width": 5,
        "height": 4,
        "fontsize": 10,
    }

The attention of :code:`--show`, :code:`--save` and :code:`--json` can be seen in :ref:`optimization <show_plot>` part.

