.. _opt_movie:

Optimization Visualize
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

One can use :program:`GVasp` to visualize the optimization trajectory, only need run the command below:

.. code-block:: bash

    gvasp movie opt

and the :file:`movie.arc` will output in the workdir.

.. _name_movie:

specify name
--------------

Certainly, if you don't like the prefix (`"movie"`), you can also specify another name to substitute it, for example,

.. code-block:: bash

    gvasp movie opt -n/--name opt.arc

then the opt.arc will output.
