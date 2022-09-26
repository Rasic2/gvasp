.. |inputs| replace:: :file:`INCAR`, :file:`KPOINTS`, :file:`POSCAR` and :file:`POTCAR`

.. _optimization:

Optimization
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Optimization is the most common task in the daily calculation work, and we now can quickly generate the inputs for optimization task with the help of :program:`GVasp`, the only need file is the :file:`*.xsd`.

When prepared the :file:`*.xsd` (from `Material Studio <https://www.3ds.com/products-services/biovia/products/molecular-modeling-simulation/biovia-materials-studio/>`_ Software) in workdir, run the command:

.. code-block:: bash

    gvasp submit opt

and the inputs (|inputs|) will be generated.

.. warning::
   The workdir should only have one \*.xsd file, otherwise, the structure generated is unknown.

.. _low:

open low-first option
----------------------

In the practical calculation, the structure optimization is time spent and one method to accelerate the optimization task can start from a low-accuracy calculation and then perform the normal calculation based the optimized low-accuracy structure.

Using :program:`GVasp`, you can run the following command to perform such low-first calculation:

.. code-block:: bash

    gvasp submit opt -l/--low

.. note::
    In fact, in the latest version, we only set the ENCUT as 300 to perform the low-accuracy calculation.

_________________________________________________

.. _arguments:

The following arguments can be applied in all of the tasks.

.. _potential:

specify potential
------------------

Certainly, if you don't like the default potential (**"PAW_PBE"**), you can also transfer a argument by specify the potential you want, like this

.. code-block:: bash

    gvasp submit opt -p/--potential PAW_PW91

.. note::
    The potential can only specify to the member of the [**'PAW_LDA'**, **'PAW_PBE'**, **'PAW_PW91'**, **'USPP_LDA'**, **'USPP_PW91'**]

.. note::
    The -p/--potential accept one or more values, if you specify one potential, all the elements will use the same potential; and if you specify two or more potentials, the potential will auto corresponding to the element in POSCAR, noticed that the number of potential should equal to the number of elements in POSCAR

.. _vdw:

open the vdw-correction
------------------------

The :program:`GVasp` support including the van der Waals (vdw) correction in calculation, just by running the following command:

.. code-block:: bash

    gvasp submit opt -V/--vdw

.. note::
    Open the vdw option will set IVDW = 12 in INCAR file.

.. _sol:

including the solvation effect
--------------------------------

The :program:`GVasp` support including the solvation effect in calculation, just by running the following command:

.. code-block:: bash

    gvasp submit opt -S/--sol

.. note::
    The default solvent is water, and you can modify it by adding EB_K argument in INCAR by yourself.

.. _gamma:

perform the Gamma-point calculation
-------------------------------------

Use single Gamma-point and vasp_gam to perform the calculation for the large-scale system can run the following command:

.. code-block:: bash

    gvasp submit opt -G/--gamma

.. _nelect:

perform charged system calculation
-------------------------------------

If you want to calculate a charged system by setting the NELECT argument, you can also use the :program:`GVasp` to generate the inputs.

Take the +1 charged system as the example, the command line can be typed as this:

.. code-block:: bash

    gvasp submit opt -N/--nelect +1

.. note::
    The NELECT accept real number as its input, so the float input (e.g., -0.5) is also allowed.

Noted that the mentioned arguments can also be used lonely or together with other arguments, like this:

.. code-block:: bash

    gvasp submit opt -G -V -S -P PAW_PBE -N/--nelect -0.5