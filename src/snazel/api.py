import logging

from snazel import builder, path
from snazel.rule import is_rule


def build(rule: str):
    if path.project_root is None:
        raise NotADirectoryError("Unable to detect a valid project root")

    logging.debug(f"found project root: {path.project_root}")

    if not is_rule(rule):
        raise ValueError(f"{rule} is not a valid rule")

    return builder.build(rule)
