.. |inputs| replace:: :file:`INCAR`, :file:`KPOINTS`, :file:`POSCAR` and :file:`POTCAR`

Generate Vasp Inputs
=================================

QVasp can help user quick generate VASP inputs (|inputs|), just need only run :file:`QVasp submit TASK [arguments]`.

All tasks accept optional [-p/-\-potential] to specify the :ref:`potential <potential>`, other arguments will describe in corresponding sub-topic.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   submit/opt
   submit/chg
   submit/dos
   submit/freq
   submit/md
   submit/stm
   submit/ts
