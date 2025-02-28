import argparse
import sys

from snazel import __app_name__, __description__, __version__


def parse():
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description=__description__,
        exit_on_error=False,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{__app_name__} {__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("rule", type=str)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("rule", type=str)

    return parser.parse_args()
