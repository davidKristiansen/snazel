import os
import sys
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from typing import  Self

import anyio

_this = sys.modules[__name__]


async def _get_git_project_root() -> os.PathLike:
    cwd = await anyio.Path.cwd()
    if await anyio.Path(cwd / ".git").is_dir():
        return cwd

    async for path in cwd.parents:
        if path is None:
            raise FileNotFoundError("no git project")
        if await anyio.Path(path / ".git").is_dir():
            return path


async def get_project_root(method: str = "git") -> os.PathLike:
    if hasattr(_this, "_project_root"):
        return _this._project_root
    match method:
        case "git":
            _this._project_root = await _get_git_project_root()
        case _:
            raise ValueError(f"Get root path with method: {method} not supported")

    return _this._project_root


class Path(anyio.Path):
    def __init__(self, *args, workdir: os.PathLike[str] | str = os.getcwd()):
        args = list(args)
        args.insert(0, anyio.Path(workdir))
        return super().__init__(*args)

    async def relative(self) -> Self:
        abs = await super().absolute()
        return abs.relative_to(await get_project_root())

    @classmethod
    async def project_root(cls) -> Self:
        return cls(await _get_git_project_root())

    @classmethod
    async def cwd(cls) -> Self:
        return cls(anyio.Path.cwd())

    def glob(self, pattern: str) -> AsyncIterator[Self]:
        gen = self._path.glob(pattern)
        return _PathIterator(gen)

    @property
    def parent(self) -> Self:
        return Path(self._path.parent)


@dataclass(eq=False)
class _PathIterator(AsyncIterator["Path"]):
    iterator: Iterator[os.PathLike[str]]

    async def __anext__(self) -> Path:
        nextval = await anyio.to_thread.run_sync(next, self.iterator, None, abandon_on_cancel=True)
        if nextval is None:
            raise StopAsyncIteration from None

        return Path(nextval)
