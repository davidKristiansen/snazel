import tomllib
import pathlib

from snazel.path import Path


with open(pathlib.Path(__file__).parent.resolve()/ "../../pyproject.toml", "rb") as f:
    data = tomllib.load(f)

__app_name__ = data["project"]["name"]
__version__ = data["project"]["version"]
__description__ = data["project"]["description"]


class MalformedRuleString(Exception):
    pass

(
    SUCCESS,
    MALFORMED_RULE_STRING,
) = range(2)

ERRORS = {
    MALFORMED_RULE_STRING: "rule string malformed"
}
