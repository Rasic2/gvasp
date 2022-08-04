.. |inputs| replace:: :file:`INCAR`, :file:`KPOINTS`, :file:`POSCAR` and :file:`POTCAR`

.. _optimization:

Optimization
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Optimization is the most common task in the daily calculation work, and we now can quickly generate the inputs for optimization task with the help of :program:`QVasp`, the only need file is the :file:`*.xsd`.

When prepared the :file:`*.xsd` (from `Material Studio <https://www.3ds.com/products-services/biovia/products/molecular-modeling-simulation/biovia-materials-studio/>`_ Software) in workdir, run the command:

.. code-block:: bash

    QVasp submit opt

and the inputs (|inputs|) will be generated.

.. warning::
   The workdir should only have one \*.xsd file, otherwise, the structure generated is unknown

.. _potential:

specify potential
------------------

Certainly, if you don't like the default potential (**"PAW_PBE"**), you can also transfer a argument by specify the potential you want, like this

.. code-block:: bash

    QVasp submit opt -p/--potential PAW_PW91

.. note::
    The potential can only specify to the member of the [**'PAW_LDA'**, **'PAW_PBE'**, **'PAW_PW91'**, **'USPP_LDA'**, **'USPP_PW91'**]

.. note::
    The -p/--potential accept one or more values, if you specify one potential, all the elements will use the same potential; and if you specify two or more potentials, the potential will auto corresponding to the element in POSCAR, noticed that the number of potential should equal to the number of elements in POSCAR
