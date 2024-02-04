from __future__ import annotations

import contextlib
import typing
from dataclasses import asdict, dataclass, field

if typing.TYPE_CHECKING:
    import pandas as pd

from .interfaces import (
    ID,
    AutomaticMetadata,
    DataBaseInterface,
    File,
    FileSystemInterface,
    IdCreatorInterface,
    ManualMetadata,
    TrackerInterface,
)


@dataclass
class Handler:
    fs: FileSystemInterface
    db: DataBaseInterface
    tracker: TrackerInterface
    id_creator: IdCreatorInterface
    based_on: list[ID] = field(default_factory=list)

    def __post_init__(self):
        self.run_id = self.id_creator.create_unique_id()

    @contextlib.contextmanager
    def create(
        self,
        relpath: str,
        automatic_metadata: AutomaticMetadata | None = None,
        manual_metadata: ManualMetadata | None = None,
    ):
        amd = automatic_metadata or self.tracker.get_automatic_metadata()
        mmd = manual_metadata or ManualMetadata()
        prefix = self.fs.define_prefix(amd)
        file = File(
            run_id=self.run_id,
            file_id=self.id_creator.create_unique_id(),
            relpath=relpath,
            remote_url=self.fs.define_remote_url(prefix, relpath),
            file_hash="",
            byte_size=0,
            automatic_metadata=amd,
            manual_metadata=mmd,
            deduplicated_by=None,
            based_on=self.based_on,
            fs=self.fs,
        )
        yield file

        file.update_hash_and_byte_size()
        self.db.save(file)

    def load(self, file_id: ID):
        file_info = self.db.load(file_id)
        while file_info.deduplicated_by:
            file_info = self.db.load(file_info.deduplicated_by)
        return File(
            **asdict(file_info),
            fs=self.fs,
        )

    def query(self, dct: dict | None = None, **kwargs) -> pd.DataFrame:
        # The type of query depends on the database
        dct = {} if dct is None else dct
        return self.db.query(dct, **kwargs)

    def deduplicate(self):
        pass
