Band Center Calculation
========================

The d-band center descriptor is widely applied in heterogeneous catalysis, and it can be calculated by the following equation:

.. math::

    \epsilon_d = \frac{\int_{-\infty}^{\infty} \epsilon\rho _d(\epsilon)d\epsilon}{\int_{-\infty}^{\infty} \rho _d(\epsilon)d\epsilon}

In :program:`GVasp`, you can easily calculated the band-center by the following command:

.. code-block:: bash

    gvasp band-center -j center.json

The center.json is like this:

.. code-block:: json

    {
      "pos_file": "CONTCAR_dos",
      "dos_file": "DOSCAR_dos",
      "atoms": "C",
      "orbitals": "p",
      "xlim": [-8.76, 11.55]
    }

The arguments in the center.json is similar with that in :ref:`dos-plot <dos_plot>` task.

.. important::
    If your LORBIT in INCAR is not 11 or 12, please add `"LORBIT": 10` in the center.json.
