.. _neb_topic:

NEB method
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

`NEB <http://theory.cm.utexas.edu/vtsttools/neb.html>`_ is a traditional method to locate the TS, which works by optimizing a number of intermediate images along the reaction path. Therefore, it's a computational cost method, while it sometimes can successfully locate TS which can't be searched by :ref:`Con-TS <con-TS>` method.

.. attention::
    Don't forget to :ref:`align the structure <align>` first.

:program:`GVasp` also support the NEB method to locate the TS, just run the command below:

.. code-block:: bash

    gvasp submit neb -ini/--ini_poscar INI_POSCAR -fni/--fni_poscar FNI_POSCAR [-i IMAGES] [-m METHOD] [-c/--cancel_check_overlap]

.. note::
    The NEB method will construct the reaction path, so one use NEB method must specify the start (**-ini/-\-ini_poscar**) and end (**-fni/-\-fni_poscar**) structure, while **-i**, **-m** and **-c** are optional arguments.

specify images
---------------

Images is the number of intermediate structures between initial and final structures, if you don't specify, :code:`images = 4` will apply.

specify method
---------------

GVasp provide two method to control how to generate the intermediate structures.

One is :code:`linear`, generate structures by linear interpolation from start to end structures.

Another is :code:`idpp` method, which declares to generate more suitable structures for NEB task, more detailed information can be seen `here <https://aip.scitation.org/doi/10.1063/1.4878664>`_.

If you don't specify the :code:`method`, GVasp will apply :code:`method = "linear"`.

check overlap
--------------

Noted that the intermediate structures generated automatically, so some atoms may overlap or closing in some cases, if you don't check, the NEB task may fail quickly.

Therefore, :program:`GVasp` check overlap always when you generate the inputs, and this behavior is also its default.

If you don't like this, you can set :code:`-c/--cancel_check_overlap` to cancel check, but we (actually I) strongly recommend you don't do this `dangerous` action.

Other arguments
-------------------

.. note::
    More information of other arguments can be seen in :ref:`optimization <arguments>` task.