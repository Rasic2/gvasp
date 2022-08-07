Setting Environment
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Display Default Environment
-------------------------------------

Default environment can display by following command:

.. code-block:: bash

    gvasp -l/--list

Initial environment is like this:

.. code-block:: bash

    ------------------------------------Configure Information---------------------------------
    ! ConfigDir:      /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp
    ! INCAR-template: /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/INCAR
    ! UValue:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/UValue.yaml
    ! PotDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/pot
    ! LogDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/logs
    ------------------------------------------------------------------------------------------

* ConfigDir: represents the directory of :file:`INCAR (template)`, :file:`UValue.yaml` and :file:`pot`

* LogDir: represents the directory of logs

* :file:`INCAR`: INCAR template file of all :program:`GVasp` submit tasks, default parameters, :download:`INCAR <./INCAR>`

* :file:`UValue.yaml`: define the UValue for elements, for example, :download:`UValue.yaml <./UValue.yaml>`

* :file:`pot`: directory of the elements' POTCAR

The structure of :file:`pot` is like this:

    .. code-block:: bash

        pot
        ├── PAW_LDA
        ├── PAW_PBE
        ├── PAW_PW91
        ├── USPP_LDA
        ├── USPP_PW91
        └── vdw_kernel.bindat


.. important::
    INCAR, UValue.yaml, pot should not be renamed




Modify Default Environment
------------------------------------

If you don't like the default environment setting, you can modify the environment by writing a config.json, the format of config.json is like this:

.. code-block:: json

    {
        "config_dir": "/your_directory_to_three_mentioned_files",
        "logdir": "/your_logs_directory",
    }


and run command:

.. code-block:: bash

    gvasp config -f config.json

Then the environment will be reset, :program:`GVasp` will auto search the :file:`INCAR`, :file:`UValue.yaml`, :file:`pot` under the config_dir.