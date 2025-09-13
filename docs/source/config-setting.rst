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

Now, user can defined their INCAR, UValue.yaml or submit.script template with the following steps:

1. Named the INCAR, UValue.yaml or submit.script template as the *.incar, *.uvalue and *.submit files, respectively.

2. Put them in your work directory or parent directory or parent's parent directory and so on directories (defined as the :code:`parent-chain`).

For example, if you want to submit a job in the :file:`/public1/home/sc81076/hzhou/M-CeO2/test` directory, the INCAR, UValue.yaml and/or submit.script template put in these directories is allowed:

.. code-block:: bash

    /public1/home/sc81076/hzhou/M-CeO2/test
    /public1/home/sc81076/hzhou/M-CeO2
    /public1/home/sc81076/hzhou/
    /public1/home/sc81076/
    /public1/home/
    /public1/
    /

After these two steps, the :program:`GVasp` :ref:`generate the inputs <generate>` will apply your templates.

.. note::
    If you have two or more templates in these directories at the same time, the :program:`GVasp` will select the directory which is nearest to the work directory.
