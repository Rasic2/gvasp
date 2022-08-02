import argparse
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qvasp: A quick post-processing process for VASP jobs")
    parser.add_argument("--task", metavar="TASK", choices=["DOS", "GRD"], type=str, help='specify the task type',
                        required=True)
    parser.add_argument("--input", metavar='dir', type=str, default=Path(".."), help="input directory")

    dos_parser = parser.add_argument_group(title='DOS calculation')
    dos_parser.add_argument("--dos-json", metavar="NAME", type=str, help="json file name")
    dos_parser.add_argument("--save", type=bool, choices=[True, False], default=True, metavar="True",
                            help="whether save the dos figure")
    dos_parser.add_argument("--format", type=str, metavar="png", choices=["png", "jpeg", "svg"], default="png",
                            help="specify figure format")

    grd_parser = parser.add_argument_group(title='GRD calculation')
    grd_parser.add_argument("--grd-name", metavar="NAME", type=str, help="grd file name")

    args = parser.parse_args()

    # check args-group
    if args.task != "DOS" and args.dos_json is not None:
        parser.error("`--dos-json` argument should not be specify in non-DOS task!")
