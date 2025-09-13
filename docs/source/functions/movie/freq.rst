.. _freq_movie:

Frequency Vibration
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

One can use :program:`GVasp` to visualize the frequency vibration, only need run the command below:

.. code-block:: bash

    gvasp movie freq

and the :file:`freq*.arc` will output in the workdir.

.. note::
    The default behavior of :program:`GVasp` will search the *image frequency* and visualize its or their vibration.

specify freq
--------------

Certainly, you can also specify the *frequency* by add the argument -f/-\-freq, and it accept :code:`'image'` (str) or :code:`int-type` (start from 0) value as the input.

.. attention::
    If you set a int value, noticed that the freq exist in your system.
