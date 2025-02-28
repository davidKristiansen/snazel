import pathlib

OVERLAYFS="fuse-overlayfs"


class OverlayFs:
    def __init__(
        self,
        lowerdir: pathlib.Path | list[pathlib.Path],
        upperdir: pathlib.Path,
        workdir: pathlib.Path,
        merged: pathlib.Path,
    ):
        for path in (upperdir, workdir, merged):
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
