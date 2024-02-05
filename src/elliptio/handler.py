from __future__ import annotations

import contextlib
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
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
    mmd: ManualMetadata | None = None

    def __post_init__(self):
        self.run_id = self.id_creator.create_unique_id(prefix="run")

    @contextlib.contextmanager
    def create(
        self,
        relpath: str,
        *,
        manual_metadata: ManualMetadata | None = None,
        automatic_metadata: AutomaticMetadata | None = None,
        save_metadata_to_filesystem: bool = True,
    ) -> Iterator[File]:
        amd = automatic_metadata or self.tracker.get_automatic_metadata()
        mmd = manual_metadata or self.mmd or ManualMetadata()
        file_id = self.id_creator.create_unique_id()
        file = File(
            file_id=file_id,
            run_id=self.run_id,
            relpath=relpath,
            remote_url=self.fs.define_remote_url(amd, file_id, relpath),
            file_hash="",
            byte_size=0,
            automatic_metadata=amd,
            manual_metadata=mmd,
            deduplicated_by=None,
            based_on=self.based_on.copy(),
            fs=self.fs,
        )
        yield file
        file.update_hash_and_byte_size()
        self.db.save(file)
        if save_metadata_to_filesystem:
            self.fs.write_text(
                remote_url=self.fs.define_remote_url(amd, file_id, ".metadata.yaml"),
                text=file.to_yaml(),
            )

    def load(self, file_id: ID) -> File:
        file_info = self.db.load(file_id)
        while file_info.deduplicated_by:
            file_info = self.db.load(file_info.deduplicated_by)
        self.based_on.append(file_info.file_id)
        return File(**asdict(file_info), fs=self.fs)

    def query(self, dct: dict | None = None, **kwargs) -> pd.DataFrame:
        # The type of query depends on the database
        dct = {} if dct is None else dct
        return self.db.query(dct, **kwargs)

    def deduplicate(self):
        # TODO: I think this shouldn't be too difficult, but done for today.
        raise NotImplementedError
