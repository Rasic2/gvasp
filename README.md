## VASP-scripts
---

This is a lot of `scripts` (not a `module`) to help post-process of the VASP calculations, and if you  want to use them, please go to the following directory and run the main function in the *.py file.

* Band (use to calculate the bandgap as well as to plot the band structure)

* Calcuator (calculated the lattice parameters and surface energy)

* **ChargeDensity** (split the charge density to `CHGCAR_tot` and `CHGCAR_mag` files; the `grd` directory including the process to tranform the `CHGCAR_mag` file to the `.grd` file, which can be loaded by the *`Material Studio`* software)

* **DOS** (use to help plot the `Density of States`, and we use **cython** (*.pyx) as the backend to load the DOSCAR file. Generally, one 100MB DOSCAR file can be easily plotted its `TDOS`, `LDOS` as well as the `PDOS` picture in 30 seconds.)

* **Frequency** (create the `*.arc` file which record the frequency vibration movie and often use to check the `imaginary frequency` in the `transtion state calculations`)

* **NEB** (when create the input POSCAR using the `xsd2in.sh` (see VaspTask directory), the atoms in IS can not corresponding to that of in FS, that is what the `neb_sort.py` do to resort the atoms in IS and FS for the following NEB calculations)

* **PES_plot** (plot the PES profile, you can easily to control the reaction process and decribe it)

* VaspTask (mainly to create the `INCAR`, `POSCAR`, `POTCAR`, `KPOINTS` and `job.script` from only `*.xsd` file)

* Temp (some temp scripts, mostly of them are useless)
---
## Notes
Mostly scripts can be run in a single *.py or *.sh file, but still some process need first to be compiled, for example, **`chgcar2grd`**.

Therefore, if you want to use them, you may compile them by yourself. Of cource, I also provide `Makefile` to help the compilation.

For example, you can compile the chgcar2grd like this:

```
cd ChargeDensity/grd;
make;
```
or
```
g++ -g -O3 chgcar2grd -c chgcar2grd.cpp
```

While for the `*.pyx` file, operation above may not work, you need to write the `setup.py` firstly, and then run the following command:
```
python setup.py build_ext --inplace
```
and the `*.so` file can be created and imported by the python.

---
## Requirements
* GNU compiler (gcc, gfortran and g++)
* Cython (use for dosPlot)




