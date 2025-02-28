import json
import anyio
import re
import hashlib
import os

import yaml

from snazel.path import Path

RULE_REGEX = r"^(\/{2})?([\w\.(\/)?]+)?:(\w+)$"

# async def from_segments(*args):
#     if len(args) == 0:
#         raise ValueError(f'{args} not valid rule segmens')
#
#     str = ""
#     if not str(args[0]).startswith("//"):
#         if await Path(args[0]).is_absolute():
#             str = "//"


def is_rule(input_str):
    return re.match(RULE_REGEX, input_str)


class Rule:
    def __init__(self, input_str, workdir: anyio.Path | None = None):
        self._prefix, self._path, self._rule_name = re.findall(RULE_REGEX, input_str)[0]
        self.workdir = workdir


        self._inputs = []
        self._dependencies = []

    async def parse(self):

        self._abs_path = (
            await Path.project_root() / self._path
            if self._prefix
            else await Path.cwd() / self._path
        )

        async with await anyio.open_file(self._abs_path / "build.yml", "rb") as f:
            content = await f.read()
        try:
            self._rule = yaml.safe_load(content)[self._rule_name]
        except KeyError:
            raise KeyError(f"no rule {str(self)}")

        print(self._rule)

        return

        dependencies: list[str] = []
        includes: list[str] = []
        for include in self._rule["srcs"]["include"]:
            if is_rule(include):
                prefix, path, rule_name = re.findall(RULE_REGEX, include)[0]
                path = project_root / path if prefix else self._abs_path / path
                dependencies.append(
                    f"//{path.relative_to(project_root)}:{rule_name}"
                )
            else:
                include = (
                    anyio.Path(os.path.expandvars(include))
                    .expanduser()
                    .resolve()
                )
                print(f"{include=}")
                if anyio.Path(include).is_absolute():
                    include = str(anyio.Path(include).relative_to(project_root))
                else:
                    include = str(self._relative_path / include)
                includes.extend(
                    [
                        f.relative_to(project_root)
                        for f in project_root.glob(include)
                    ]
                )

        excludes = []
        if "exclude" in self._rule["srcs"]:
            for exclude in self._rule["srcs"]["exclude"]:
                exclude = (
                    anyio.Path(os.path.expandvars(exclude))
                    .expanduser()
                    .resolve()
                )
                if anyio.Path(include).is_absolute():
                    exclude = str(anyio.Path(exclude).relative_to(project_root))
                else:
                    exclude = str(self._relative_path / exclude)
                excludes.extend(
                    [
                        f.relative_to(project_root)
                        for f in project_root.glob(exclude)
                    ]
                )

        self._inputs = sorted(
            set(
                [
                    i
                    for i in includes
                    if i not in excludes and os.path.isfile(project_root / i)
                ]
            )
        )
        self._dependencies = sorted(set([i for i in dependencies]))

    def __str__(self) -> str:
        return f"//{self._relative_path}:{self._rule_name}"

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def relative_path(self) -> anyio.Path:
        return self._abs_path.relative_to(project_root)

    @property
    async def hash(self, hash_algorithm: str = "sha256") -> str:
        if not hasattr(self, "_hash"):
            hash_func = hashlib.new(hash_algorithm)

            rule = json.dumps(self._rule, sort_keys=True, separators=(",", ":"))

            hash_func.update(rule.encode("utf-8"))

            for dependency in self._dependencies:
                hash_func.update(str(dependency).encode("utf-8"))

            for file in self._inputs:
                hash_func.update(str(file).encode("utf-8"))

                with open(project_root / file, "rb") as f:
                    while chunk := f.read(8192):
                        hash_func.update(chunk)

            self._hash = hash_func.hexdigest()

        return self._hash
