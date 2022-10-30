import argparse
import json
import logging
import os
import shutil
import stat
import sys
import traceback
from pathlib import Path
from typing import Iterable

from common.calculator import surface_energy, electrostatic_energy
from gvasp.common.constant import RED, RESET, Version, Platform, GREEN, YELLOW
from gvasp.common.figure import Figure
from gvasp.common.file import POTENTIAL
from gvasp.common.logger import init_root_logger
from gvasp.common.plot import PlotOpt, PlotBand, PlotNEB, PlotPES, PlotDOS, PlotEPotential
from gvasp.common.setting import ConfigManager, RootDir, HomeDir
from gvasp.common.task import OptTask, ConTSTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, NEBTask, DimerTask, \
    SequentialTask, OutputTask, WorkFuncTask
from gvasp.common.utils import colors_generator

logger = logging.getLogger(__name__)


def main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="GVasp: A quick post-process for resolve or assistant the VASP calculations")
    parser.add_argument("-v", "--version", help="version information", action="store_true")
    parser.add_argument("-l", "--list", help="list environment setting", action="store_true")
    subparsers = parser.add_subparsers()

    # config parser
    config_parser = subparsers.add_parser(name='config', help="modify the default environment")
    config_parser.add_argument("-f", "--file", type=str, help='specify the location of config.json', required=True)
    config_parser.set_defaults(which='config')

    # submit parser
    submit_parser = subparsers.add_parser(name="submit", help="generate inputs for special job-task")
    submit_parser.add_argument("task",
                               choices=["opt", "con-TS", "chg", "wf", "dos", "freq", "md", "stm", "neb", "dimer"],
                               type=str, help='specify job type for submit')
    submit_parser.add_argument("-P", "--potential", metavar="POTENTIAL", default="PAW_PBE", nargs="+", type=str,
                               help=f'specify potential, optional: {POTENTIAL}')
    submit_parser.add_argument("-V", "--vdw", help=f'add vdw-correction', action='store_true')
    submit_parser.add_argument("-S", "--sol", help=f'perform solvation calculation', action='store_true')
    submit_parser.add_argument("-G", "--gamma", help=f'perform Gamma-point calculation', action='store_true')
    submit_parser.add_argument("-N", "--nelect", help=f'specify the system charge', type=float)
    submit_parser.add_argument("-C", "--continuous", help=f'calculation from finished job', action='store_true')

    low_group = submit_parser.add_argument_group(title='low-task',
                                                 description='only valid for opt and sequential [chg, wf, dos] tasks')
    low_group.add_argument("-l", "--low", help="specify whether perform low-accuracy calculation first",
                           action="store_true")

    sequential_group = submit_parser.add_argument_group(title='sequential-task',
                                                        description='only valid for [chg, wf, dos] tasks')
    sequential_group.add_argument("-s", "--sequential", help='whether or not sequential', action="store_true")

    charge_group = submit_parser.add_argument_group(title='charge-task',
                                                    description='only valid for chg and sequential [chg, dos] tasks')
    charge_group.add_argument("-a", "--analysis", help='whether or not apply bader calculation && split CHGCAR',
                              action="store_true")

    neb_submit_group = submit_parser.add_argument_group(title='neb-task')
    neb_submit_group.add_argument("-ini", "--ini_poscar", type=str, help='specify ini poscar for neb task')
    neb_submit_group.add_argument("-fni", "--fni_poscar", type=str, help='specify fni poscar for neb task')
    neb_submit_group.add_argument("-i", "--images", type=int, help='specify the neb images')
    neb_submit_group.add_argument("-m", "--method", type=str, choices=['linear', 'idpp'],
                                  help='specify the method to generate neb images')
    neb_submit_group.add_argument("-c", "--cancel_check_overlap", action='store_true',
                                  help='whether or not check_overlap')
    submit_parser.set_defaults(which="submit")

    # output parser
    output_parser = subparsers.add_parser(name="output", help="output to .xsd file")
    output_parser.set_defaults(which="output")

    # movie parser
    movie_parser = subparsers.add_parser(name="movie", help="visualize the trajectory")
    movie_parser.add_argument("task", choices=["opt", "con-TS", "freq", "md", "neb", "dimer"], type=str,
                              help='specify job type for movie')
    movie_parser.add_argument("-n", "--name", default="movie.arc", type=str, help='specify name of *.arc')
    freq_movie_group = movie_parser.add_argument_group(title='freq-task')
    freq_movie_group.add_argument("-f", "--freq", default='image', help='specify freq index')
    neb_movie_group = movie_parser.add_argument_group(title='neb-task')
    neb_movie_group.add_argument("-p", "--pos", default='CONTCAR', help='which type of file to generate neb movie')
    movie_parser.set_defaults(which="movie")

    # sort parser
    sort_parser = subparsers.add_parser(name="sort", help="sort two POSCAR for neb task submit")
    sort_parser.add_argument("-ini", "--ini_poscar", type=str, help='specify ini poscar for neb task')
    sort_parser.add_argument("-fni", "--fni_poscar", type=str, help='specify fni poscar for neb task')
    sort_parser.set_defaults(which="sort")

    # plot parser
    plot_parser = subparsers.add_parser(name='plot', help="plot DOS, BandStructure, PES and so on")
    plot_parser.add_argument("task", choices=['opt', 'band', 'ep', 'dos', 'PES', 'neb'], type=str,
                             help='specify job type for plot')
    plot_parser.add_argument("-j", "--json", type=str, help='*.json file to quick setting', required=True)
    plot_parser.add_argument("-n", "--name", type=str, default="figure.svg", help='specify name of dos plot figure')
    display_plot_group = plot_parser.add_mutually_exclusive_group()
    display_plot_group.add_argument("--show", action='store_true', help='show figure')
    display_plot_group.add_argument("--save", action='store_true', help='save figure')
    plot_parser.set_defaults(which='plot')

    # band-center parser
    band_center_parser = subparsers.add_parser(name="band-center", help="calculate the band-center of the DOS")
    band_center_parser.add_argument("-j", "--json", type=str, help='*.json file to quick setting', required=True)
    band_center_parser.set_defaults(which="band-center")

    # sum parser
    sum_parser = subparsers.add_parser(name="sum", help="sum AECCAR0 and AECCAR2 to CHGCAR_sum")
    sum_parser.set_defaults(which="sum")

    # split parser
    split_parser = subparsers.add_parser(name="split", help="split CHGCAR to CHGCAR_mag and CHGCAR_tot")
    split_parser.set_defaults(which="split")

    # grd parser
    grd_parser = subparsers.add_parser(name="grd", help="transform CHGCAR_mag to *.grd file")
    grd_parser.add_argument("-n", "--name", default="vasp.grd", type=str, help="specify the name of *.grd")
    grd_parser.add_argument("-d", "--DenCut", default=250, type=int, help="specify the cutoff density")
    grd_parser.set_defaults(which="grd")

    # calc parser
    calc_parser = subparsers.add_parser(name="calc", help="various calculation utils")
    calc_parser.add_argument("task", type=int, help="specify task-order (0-[surface energy]; 1-[electrostatic energy])")
    surf_calc_group = calc_parser.add_argument_group(title='surface energy calculation')
    surf_calc_group.add_argument("-c", "--crystal_dir", type=str, help='specify crystal directory')
    surf_calc_group.add_argument("-s", "--slab_dir", type=str, help='specify slab directory')
    electrostatic_calc_group = calc_parser.add_argument_group(title='electrostatic energy calculation')
    electrostatic_calc_group.add_argument("-a", "--atoms", nargs="+", help="specify the atoms")
    electrostatic_calc_group.add_argument("-w", "--workdir", default=".", help="specify the workdir")
    calc_parser.set_defaults(which="calc")

    return parser


def main_completion():
    if 'Linux' in Platform and not (Path(HomeDir) / ".gvasp-completion").exists():
        shutil.copy(Path(RootDir) / "gvasp-bash-completion.sh", Path(HomeDir) / ".gvasp-completion")
        with open(Path(HomeDir) / ".bash_completion", "a+") as f:
            f.write("source ~/.gvasp-completion \n")


def main_permission():
    files_read_only = ['config.json', 'element.yaml', 'gvasp-bash-completion.sh', 'INCAR', 'slurm.submit',
                       'UValue.yaml']
    for file in files_read_only:
        if os.access(Path(RootDir) / file, os.W_OK):
            os.chmod(Path(RootDir) / file, stat.S_IRUSR)


def exception_format(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            exc_type, exc_value, exc_obj = sys.exc_info()
            exc_location = traceback.format_exc(limit=-1).splitlines()[1]
            print(f"+{'Error'.center(len(exc_location) + 30, '-')}\n"
                  f"| exception_location:     {RED}{exc_location.lstrip()}{RESET} \n"
                  f"| exception_type:         {GREEN}{exc_type}{RESET} \n"
                  f"| exception_value:        {YELLOW}{exc_value}{RESET}\n"
                  f"+{'-----'.center(len(exc_location) + 30, '-')}")

    return wrapper


@exception_format
def main(argv=None):
    init_root_logger(name="gvasp")

    main_completion()  # set auto-completion
    main_permission()  # modify file permission

    Config = ConfigManager()
    parser = main_parser()

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if len(sys.argv) == 1:
        parser.print_help()

    # version output
    if args.version:
        print(f"GVasp version {Version} ({Platform})")

    # print configure information
    if args.list:
        print(Config)

    if "which" in args:
        if args.which == 'config':  # reset the environment
            print(f"1. Start Change environment setting, file is: {Path(args.file)}")
            print(f"2. Load {Path(args.file)}")
            with open(Path(args.file)) as f:
                new_config = json.load(f)
            print(f"3. Substitute {RootDir}/config.json with {Path(args.file)}")
            for key in Config.dict.keys():
                if new_config.get(key, None) is not None:
                    setattr(Config, key, new_config[key])
            Config.write()
            print(f"4. Print the new configure information")
            print(Config)
            print(f"5. Reset Done")

        elif args.which == 'submit':  # submit task
            normal_tasks = {"con-TS": ConTSTask().generate,
                            "freq": FreqTask().generate,
                            "md": MDTask().generate,
                            "stm": STMTask().generate,
                            "dimer": DimerTask().generate}

            normal_kargs = {"potential": args.potential,
                            "vdw": args.vdw,
                            "sol": args.sol,
                            "gamma": args.gamma,
                            "nelect": args.nelect}

            if args.task in normal_tasks.keys():
                logger.info(f"generate `{args.task}` task")
                normal_tasks[args.task](**normal_kargs)
            elif args.task == "opt":
                logger.info(f"generate `opt` task")
                OptTask().generate(continuous=args.continuous, low=args.low, **normal_kargs)
            elif args.task == "chg":
                if args.sequential:
                    SequentialTask(end="chg").generate(low=args.low, analysis=args.analysis, **normal_kargs)
                else:
                    logger.info(f"generate `chg` task")
                    ChargeTask().generate(continuous=args.continuous, analysis=args.analysis, **normal_kargs)
            elif args.task == "wf":
                if args.sequential:
                    SequentialTask(end="wf").generate(low=args.low, **normal_kargs)
                else:
                    logger.info(f"generate `wf` task")
                    WorkFuncTask().generate(continuous=args.continuous, **normal_kargs)
            elif args.task == "dos":
                if args.sequential:
                    SequentialTask(end="dos").generate(low=args.low, analysis=args.analysis, **normal_kargs)
                else:
                    logger.info(f"generate `dos` task")
                    DOSTask().generate(continuous=args.continuous, **normal_kargs)
            elif args.task == "neb":
                if args.ini_poscar is None or args.fni_poscar is None:
                    raise AttributeError(None, "ini_poscar and fni_poscar arguments must be set!")
                args.images = 4 if args.images is None else args.images
                args.method = "linear" if args.method is None else args.method

                print(f"Your neb submit task arguments is: ")
                print(f"    ini_poscar = {args.ini_poscar}")
                print(f"    fni_poscar = {args.fni_poscar}")
                print(f"    images = {args.images}")
                print(f"    method = {args.method}")
                print(f"    potential = {args.potential}")
                print(f"    check_overlap = {not args.cancel_check_overlap}")

                check = input(f"Please confirm or cancel (y/n): ")
                if check.lower()[0] == "y":
                    NEBTask(ini_poscar=args.ini_poscar, fni_poscar=args.fni_poscar, images=args.images).generate(
                        method=args.method, check_overlap=not args.cancel_check_overlap, **normal_kargs)
                else:
                    print(f"Cancel neb task")

        elif args.which == 'output':  # output task
            with open("submit.script", "r") as f:
                content = f.readlines()
            name = content[1].split()[2]
            OutputTask.output(name=f"{name}.xsd")
            logger.info(f"{RED}transform to {name}.xsd file{RESET}")

        elif args.which == 'movie':  # movie task
            normal_tasks = {"opt": OptTask.movie,
                            "con-TS": ConTSTask.movie,
                            "md": MDTask.movie,
                            "dimer": DimerTask.movie
                            }
            if args.task in normal_tasks.keys():
                logger.info(f"`{args.task}` task movie")
                normal_tasks[args.task](name=args.name)

            if args.task == 'freq':
                FreqTask.movie(freq=args.freq)

            if args.task == 'neb':
                NEBTask.movie(name=args.name, file=args.pos)

        elif args.which == 'sort':  # sort task
            if args.ini_poscar is None or args.fni_poscar is None:
                raise AttributeError(None, "ini_poscar and fni_poscar arguments must be set!")
            NEBTask.sort(ini_poscar=args.ini_poscar, fni_poscar=args.fni_poscar)

        elif args.which == 'plot':  # plot task

            # load json file to read setting and data
            with open(args.json, "r") as f:
                arguments = json.load(f)

            # record color lack
            color_lack = False
            if args.task != "dos" and 'color' not in arguments:
                arguments['color'] = '#000000'
                logger.warning(f"color argument is not exist in {args.json}, use default value")
                color_lack = True

            if args.task != "dos":
                colors = arguments['color']
                del arguments['color']

            if args.task == 'opt':
                plotter = PlotOpt(**arguments)
                if color_lack:
                    colors = ("#ed0345", "#009734")
                plotter.plot(color=colors)
            elif args.task == 'ep':
                plotter = PlotEPotential(**arguments)
                plotter.plot()
            elif args.task == 'band':
                plotter = PlotBand(**arguments)
                plotter.plot()
            elif args.task == 'dos':
                if not isinstance(arguments['dos_file'], list) or not isinstance(arguments['pos_file'], list):
                    raise TypeError("`dos_file` and `pos_file` arguments should be a list")

                assert len(arguments['dos_file']) == len(arguments['pos_file']), \
                    "The length of `dos_file` and `pos_file` is not match"

                if 'data' not in arguments:
                    raise AttributeError(None, f"`data` arguments should exist")

                dos_files, pos_files = arguments['dos_file'], arguments['pos_file']
                data = arguments['data']
                del arguments['dos_file']
                del arguments['pos_file']
                del arguments['data']

                plotters = [PlotDOS(dos_file, pos_file, **arguments) for dos_file, pos_file in
                            zip(dos_files, pos_files)]
                for key in data.keys():
                    for line_argument in data[key]:
                        plotters[int(key)].plot(**line_argument)

            elif args.task == 'PES':

                if not isinstance(arguments['data'][0], Iterable):
                    raise AttributeError(None, "`data` arguments should be a list of lines")

                if 'text_flag' not in arguments:
                    arguments['text_flag'] = True
                    logger.warning(f"text_flag argument is not exist in {args.json}, use default value")

                if 'style' not in arguments:
                    arguments['style'] = "solid_dash"
                    logger.warning(f"style argument is not exist in {args.json}, use default value")

                if color_lack:
                    colors = colors_generator()

                plotter = PlotPES(**arguments)
                for data, color in zip(arguments['data'], colors):
                    plotter.plot(data=data, color=color, text_flag=arguments['text_flag'], style=arguments['style'])
            elif args.task == 'neb':
                plotter = PlotNEB(**arguments)
                plotter.plot(color=colors)

            if args.show:
                if "linux" in Platform.lower():
                    logger.warning(f"Linux platform may not support figure `show`, if fail, use `save` substitute")
                Figure.show()
            if args.save:
                Figure.save(name=args.name)
                logger.info(f"Figure has been saved as `{args.name}`, please check")

        elif args.which == 'band-center':  # band-center task
            with open(args.json, "r") as f:  # load json file to read setting and data
                arguments = json.load(f)

            if "pos_file" not in arguments:
                arguments['pos_file'] = "CONTCAR"
            if "dos_file" not in arguments:
                arguments['dos_file'] = "DOSCAR"

            post_dos = PlotDOS(dos_file=arguments['dos_file'], pos_file=arguments['pos_file'])
            post_dos.center(atoms=arguments['atoms'], orbitals=arguments['orbitals'], xlim=arguments['xlim'])

        elif args.which == 'sum':  # sum task
            ChargeTask.sum()

        elif args.which == 'split':  # split task
            ChargeTask.split()

        elif args.which == 'grd':  # grd task
            ChargeTask.to_grd(name=args.name, Dencut=args.DenCut)

        elif args.which == 'calc':  # calculation utils task
            if args.task == 0:
                surface_energy(crystal_dir=args.crystal_dir, slab_dir=args.slab_dir)
            elif args.task == 1:
                electrostatic_energy(atoms=args.atoms, workdir=args.workdir)
