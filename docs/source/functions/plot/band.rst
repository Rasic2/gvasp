Band Structure Plot
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

For the band structure, one can use :program:`GVasp` to plot it, just run the command:

.. code-block:: bash

    gvasp plot band -j plot.json --save

then, one may obtain the :file:`figure.svg` which plot the band structure.

Just like this,

.. image:: band.svg
   :align: center
   :width: 400

.. note::
    In the current version, the presence of a :file:`KPATH.in` file (from VASPKIT) in the working directory determines the high-symmetry points used:
    if it exists, those points are utilized; otherwise, a default path is used.

For this task, the :file:`plot.json` is like this

.. code-block:: json

    {
        "title": "Band Structure",
        "ylim": [-6, 4],
        "ylabel": "Energy (eV)",
        "bwidth": 2,
        "xlim": [0, 147],
        "xticks": []
    }

The attention of :code:`--show`, :code:`--save` and :code:`--json` can be seen in :ref:`optimization <show_plot>` part.

