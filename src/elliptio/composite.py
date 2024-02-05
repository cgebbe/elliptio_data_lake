from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from elliptio.adapters.db import SqlDatabase
from elliptio.adapters.fs import FsspecFilesystem
from elliptio.adapters.id_creator import IdCreator
from elliptio.adapters.tracker import Tracker
from elliptio.handler import Handler

if TYPE_CHECKING:
    from elliptio.interfaces import (
        DataBaseInterface,
        FileSystemInterface,
        IdCreatorInterface,
        ManualMetadata,
        TrackerInterface,
    )


class DirectoryDoesNotExistError(ValueError):
    def __init__(self, dirpath: Path | str) -> None:
        super().__init__(f"{dirpath=} does not exist.")


def get_handler(  # noqa: PLR0913
    *,
    dirpath: Path | str | None = None,
    fs: FileSystemInterface | None = None,
    db: DataBaseInterface | None = None,
    tracker: TrackerInterface | None = None,
    id_creator: IdCreatorInterface | None = None,
    manual_metadata: ManualMetadata | None = None,
) -> Handler:
    if dirpath is not None and not Path(dirpath).exists():
        raise DirectoryDoesNotExistError(dirpath)

    return Handler(
        fs=fs or FsspecFilesystem(str(dirpath)),
        db=db or SqlDatabase(Path(dirpath) / "db.sqlite"),  # type: ignore [arg-type]
        tracker=tracker or Tracker(),
        id_creator=id_creator or IdCreator(),
        mmd=manual_metadata,
    )
