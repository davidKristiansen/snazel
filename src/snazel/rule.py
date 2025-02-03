import json
import pathlib
import re
import hashlib
import os

import yaml

from snazel.path import cwd, project_root

RULE_REGEX = r"^(\/{2})?([\w\.(\/)?]+)?:(\w+)$"


def is_rule(input_str):
    return re.match(RULE_REGEX, input_str)


class Rule:
    def __init__(self, input_str, workdir: pathlib.Path = cwd):
        prefix, path, self.rule_name = re.findall(RULE_REGEX, input_str)[0]

        self.abs_path = project_root / path if prefix else cwd / path

        self._parse()

    def _parse(self):
        with open(self.abs_path / "build.yml", "rb") as f:
            try:
                self._rule = yaml.safe_load(f)[self.rule_name]
            except KeyError:
                raise KeyError(f"no rule {str(self)}")

        dependencies: list[str] = []
        includes: list[str] = []
        for include in self._rule["srcs"]["include"]:
            if is_rule(include):
                prefix, path, rule_name = re.findall(RULE_REGEX, include)[0]
                path = project_root / path if prefix else self.abs_path / path
                dependencies.append(f"//{path.relative_to(project_root)}:{rule_name}")
            else:
                if pathlib.Path(include).is_absolute():
                    include = str(pathlib.Path(include).relative_to(project_root))
                else:
                    include = str(self.path / include)
                includes.extend([f.relative_to(project_root) for f in project_root.glob(include)])

        excludes = []
        if "exclude" in self._rule["srcs"]:
            for exclude in self._rule["srcs"]["exclude"]:
                if pathlib.Path(include).is_absolute():
                    exclude = str(pathlib.Path(exclude).relative_to(project_root))
                else:
                    exclude = str(self.path / exclude)
                excludes.extend([f.relative_to(project_root) for f in project_root.glob(exclude)])

        self.inputs = sorted(set([i for i in includes if i not in excludes and os.path.isfile(project_root / i)]))
        self._dependencies = sorted(set([i for i in dependencies]))

    def __str__(self) -> str:
        return f"//{self.path}:{self.rule_name}"

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def path(self) -> pathlib.Path:
        return self.abs_path.relative_to(project_root)

    @property
    def hash(self, hash_algorithm: str = "sha256") -> str:
        hash_func = hashlib.new(hash_algorithm)

        rule = json.dumps(self._rule, sort_keys=True, separators=(",", ":"))

        hash_func.update(rule.encode("utf-8"))

        for dependency in self._dependencies:
            hash_func.update(str(dependency).encode("utf-8"))

        for file in self.inputs:
            hash_func.update(str(file).encode("utf-8"))

            with open(project_root / file, "rb") as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)

        return hash_func.hexdigest()
