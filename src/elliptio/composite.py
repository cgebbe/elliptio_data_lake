from pathlib import Path

from elliptio.adapters import db, fs, id_creator, tracker
from elliptio.handler import Handler


def get_default_handler(dirpath: Path) -> Handler:
    return Handler(
        fs=fs.FsspecFilesys(str(dirpath)),
        db=db.SqlDatabase(dirpath / "db.sqlite"),
        tracker=tracker.Tracker(),
        id_creator=id_creator.IdCreator(),
    )
