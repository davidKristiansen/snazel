import logging

from snazel import api
from snazel.cli.args import parse as parse_args


def run():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose > 0 else logging.INFO)

    match args.cmd:
        case "build":
            api.build(args.rule)
        case _:
            raise NotImplementedError(f"{args.cmd} not implemented")

