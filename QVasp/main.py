import argparse
import json
from argparse import ArgumentError
from pathlib import Path

import argcomplete

from common.setting import Config, RootDir, Version, Platform


def main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QVasp: A quick post-process for resolve or assistant the VASP calculations")
    parser.add_argument("-v", "--version", help="version information", action="store_true")
    parser.add_argument("-l", "--list", help="list environment setting", action="store_true")
    subparsers = parser.add_subparsers()

    config_parser = subparsers.add_parser(name='config', help="modify the default environment")
    config_parser.add_argument("-f", "--file", type=str, help='specify the location of config.json', required=True)
    config_parser.set_defaults(which='config')

    submit_parser = subparsers.add_parser(name="submit", help="generate inputs for special job-task")
    submit_parser.add_argument("task", choices=["opt", "con-TS", "chg", "dos", "freq", "md", "stm", "neb", "dimer"],
                               type=str, help='specify job type for submit')
    submit_parser.set_defaults(which="submit")

    movie_parser = subparsers.add_parser(name="movie", help="visualize the trajectory")
    movie_parser.add_argument("task", choices=["opt", "con-TS", "freq", "md", "neb", "dimer"], type=str,
                              help='specify job type for movie')
    movie_parser.add_argument("-f", "--freq", help='specify freq index')
    movie_parser.set_defaults(which="movie")

    plot_parser = subparsers.add_parser(name='plot', help="plot DOS, BandStructure, PES and so on")
    plot_parser.add_argument("task", choices=['opt', 'band', 'dos', 'PES', 'NEB'], type=str,
                             help='specify job type for plot')
    plot_parser.set_defaults(which='plot')

    sum_parser = subparsers.add_parser(name="sum", help="sum AECCAR0 and AECCAR2 to CHGCAR_sum")
    sum_parser.set_defaults(which="sum")

    split_parser = subparsers.add_parser(name="split", help="split CHGCAR to CHGCAR_mag and CHGCAR_tot")
    split_parser.set_defaults(which="split")

    grd_parser = subparsers.add_parser(name="grd", help="transform CHGCAR_mag to *.grd file")
    grd_parser.set_defaults(which="grd")

    return parser


def main():
    parser = main_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

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

        if args.which == 'movie' and args.task != 'freq' and args.freq is not None:  # check `freq` argument
            raise ArgumentError(None, "freq argument is only valid for movie::freq task")


if __name__ == "__main__":
    main()
