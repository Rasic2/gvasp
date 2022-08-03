import argparse
import json
import sys
from argparse import ArgumentError
from pathlib import Path

from QVasp.common.task import OptTask, ConTSTask, ChargeTask, DOSTask, FreqTask, MDTask, STMTask, NEBTask, DimerTask
from common.file import POTENTIAL
from common.logger import logger
from common.plot import PlotOpt, PlotBand, PlotNEB
from common.setting import Config, RootDir, Version, Platform


def main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QVasp: A quick post-process for resolve or assistant the VASP calculations")
    parser.add_argument("-v", "--version", help="version information", action="store_true")
    parser.add_argument("-l", "--list", help="list environment setting", action="store_true")
    subparsers = parser.add_subparsers()

    # config parser
    config_parser = subparsers.add_parser(name='config', help="modify the default environment")
    config_parser.add_argument("-f", "--file", type=str, help='specify the location of config.json', required=True)
    config_parser.set_defaults(which='config')

    # submit parser
    submit_parser = subparsers.add_parser(name="submit", help="generate inputs for special job-task")
    submit_parser.add_argument("task", choices=["opt", "con-TS", "chg", "dos", "freq", "md", "stm", "neb", "dimer"],
                               type=str, help='specify job type for submit')
    submit_parser.add_argument("-p", "--potential", metavar="POTENTIAL", default="PAW_PBE", nargs="+",
                               choices=POTENTIAL, type=str, help='specify potential')
    neb_submit_group = submit_parser.add_argument_group(title='neb-task')
    neb_submit_group.add_argument("--ini_poscar", type=str, help='specify ini poscar for neb task')
    neb_submit_group.add_argument("--fni_poscar", type=str, help='specify fni poscar for neb task')
    neb_submit_group.add_argument("-i", "--images", type=int, help='specify the neb images')
    neb_submit_group.add_argument("-m", "--method", type=str, choices=['linear', 'idpp'],
                                  help='specify the method to generate neb images')
    neb_submit_group.add_argument("-c", "--cancel_check_overlap", action='store_true',
                                  help='whether or not check_overlap')
    submit_parser.set_defaults(which="submit")

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
    sort_parser.add_argument("--ini_poscar", type=str, help='specify ini poscar for neb task')
    sort_parser.add_argument("--fni_poscar", type=str, help='specify fni poscar for neb task')
    sort_parser.set_defaults(which="sort")

    # plot parser
    plot_parser = subparsers.add_parser(name='plot', help="plot DOS, BandStructure, PES and so on")
    plot_parser.add_argument("task", choices=['opt', 'band', 'dos', 'PES', 'neb'], type=str,
                             help='specify job type for plot')
    plot_parser.add_argument("-n", "--name", type=str, help='specify file to load')
    plot_parser.add_argument("-w", "--width", type=float, help='specify the width of figure')
    plot_parser.add_argument("-t", "--title", type=str, help='specify the title of figure')
    plot_parser.add_argument("--xlabel", type=str, help='specify the xlabel of figure')
    plot_parser.add_argument("--ylabel", type=str, help='specify the ylabel of figure')
    plot_parser.add_argument("-c", "--color", default='#000000', nargs='+', help='specify the color')
    display_plot_group = plot_parser.add_mutually_exclusive_group(title='figure display')
    display_plot_group.add_argument("--show", action='store_true', help='show figure')
    display_plot_group.add_argument("--save", action='store_true', help='save figure as figure.svg')
    plot_parser.set_defaults(which='plot')

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

    return parser


def main():
    parser = main_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    # version output
    if args.version:
        print(f"QVasp version {Version} ({Platform})")

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
                if getattr(new_config, key, None) is not None:
                    Config[key] = new_config[key]
            print(f"4. Print the new configure information")
            print(Config)
            print(f"5. Reset Done")

        elif args.which == 'submit':  # submit task
            ordinary = {"opt": OptTask().generate,
                        "con-TS": ConTSTask().generate,
                        "chg": ChargeTask().generate,
                        "dos": DOSTask().generate,
                        "freq": FreqTask().generate,
                        "md": MDTask().generate,
                        "stm": STMTask().generate,
                        "dimer": DimerTask().generate}

            if args.task in ordinary.keys():
                logger.info(f"generate `{args.task}` task")
                ordinary[args.task](potential=args.potential)
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
                        method=args.method, potential=args.potential, check_overlap=not args.cancel_check_overlap)
                else:
                    print(f"Cancel neb task")

        elif args.which == 'movie':  # movie task
            ordinary = {"opt": OptTask.movie,
                        "con-TS": ConTSTask.movie,
                        "md": MDTask.movie,
                        "dimer": DimerTask.movie
                        }
            if args.task in ordinary.keys():
                logger.info(f"`{args.task}` task movie")
                ordinary[args.task](name=args.name)

            if args.task == 'freq':
                FreqTask.movie(freq=args.freq)

            if args.task == 'neb':
                NEBTask.movie(name=args.name, file=args.file)

        elif args.which == 'sort':  # sort task
            if args.ini_poscar is None or args.fni_poscar is None:
                raise AttributeError(None, "ini_poscar and fni_poscar arguments must be set!")
            NEBTask.sort(ini_poscar=args.ini_poscar, fni_poscar=args.fni_poscar)

        elif args.which == 'plot':  # plot task
            if args.task == 'opt':
                arguments = {'name': args.name, 'width': args.width, 'title': args.title, 'xlabel': args.xlabel, }
                arguments = {key: value for key, value in arguments.items() if value is not None}
                plotter = PlotOpt(**arguments)
                plotter.plot(color=args.color)
            elif args.task == 'band':
                arguments = {'name': args.name, 'title': args.title}
                arguments = {key: value for key, value in arguments.items() if value is not None}
                plotter = PlotBand(**arguments)
                plotter.plot()
            elif args.task == 'dos':
                pass
            elif args.task == 'PES':
                pass
            elif args.task == 'neb':
                arguments = {'width': args.width, 'xlabel': args.xlabel, 'ylabel': args.ylabel}
                arguments = {key: value for key, value in arguments.items() if value is not None}
                plotter = PlotNEB(**arguments)
                plotter.plot(color=args.color)
            else:
                raise AttributeError(None, f"{args.task} is not supported")

            if args.show:
                plotter.show()
            if args.save:
                plotter.save()

        elif args.which == 'sum':  # sum task
            ChargeTask.sum()

        elif args.which == 'split':  # split task
            ChargeTask.split()

        elif args.which == 'grd':  # grd task
            ChargeTask.to_grd(name=args.name, Dencut=args.DenCut)


if __name__ == "__main__":
    main()
