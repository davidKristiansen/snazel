import pathlib
from dataclasses import dataclass


def _get_git_project_root() -> pathlib.Path:
    if pathlib.Path(cwd / ".git").is_dir():
        return cwd

    for path in pathlib.Path(cwd).parents:
        if path is None:
            raise FileNotFoundError("no git project")
        if pathlib.Path(path / ".git").is_dir():
            return path


def get_project_root(method: str = "git") -> pathlib.Path:
    match method:
        case "git":
            return _get_git_project_root()
        case _:
            raise ValueError(f"Get root path with method: {method} not supported")

cwd = pathlib.Path.cwd()
project_root = get_project_root()

@dataclass
class Path:
    current_working_dir: pathlib.Path = pathlib.Path.cwd()
    project_root: pathlib.Path = get_project_root()

    @property
    def relative_to_root(self):
        return self.current_working_dir.relative_to(self.project_root)

    def __str__(self):
        print(self.relative_to_root)
