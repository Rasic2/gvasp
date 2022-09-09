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
    ! scheduler:      slurm
    ! PotDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/pot
    ! LogDir:         /mnt/c/Users/hui_zhou/Desktop/packages/gvasp/gvasp/logs
    ------------------------------------------------------------------------------------------

* ConfigDir: represents the directory of :file:`INCAR (template)`, :file:`UValue.yaml` and :file:`pot`

* scheduler: represents the job control system, now only support the slurm (but you can specify a .submit file in your parent-chain path, see :ref:`here <user_template>`)

* LogDir: represents the directory of logs

* :file:`INCAR`: INCAR template file of all :program:`GVasp` submit tasks, default parameters, :download:`INCAR <./INCAR>`

* :file:`UValue.yaml`: define the UValue for elements, for example, :download:`UValue.yaml <./UValue.yaml>`

* :file:`pot`: directory of the elements' POTCAR (please prepare it by yourself)

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
      "potdir": "/your_pot_directory",
      "logdir": "/your_logs_directory"
    }


and run command:

.. code-block:: bash

    gvasp config -f config.json

Then the environment will be reset, :program:`GVasp` will auto search the :file:`INCAR` and :file:`UValue.yaml` under the config_dir.

.. _user_template:

User template
----------------

Now, user can defined their incar or submit template with the following steps:

1. Named the incar or submit template as the *.incar and *.submit files.

2. Put them in your parent or parent's parent and so on directories (defined as the :code:`parent-chain`).

After these two steps, the :program:`GVasp` :ref:`generate the inputs <generate>` will apply your templates.