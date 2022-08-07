.. _neb_movie:

NEB Method
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

For NEB method, we actually support to visualize the reaction path by concentrate its images' :file:`POSCARs` or :file:`CONTCARs`, and likewise the other task, one can do this by:

.. code-block:: bash

    gvasp movie neb

and the :file:`movie.arc` will output in the workdir.


specify position
-----------------

Through the -p/-\-pos argument, You can choose which type of files to construct the *reaction path*, i.e., :file:`POSCAR` or :file:`CONTCAR`, default type is :file:`POSCAR`.

specify name
--------------

Certainly, if you don't like the prefix (`"movie"`), you can also specify another name to substitute it, likewise the :ref:`optimization <name_movie>` task.