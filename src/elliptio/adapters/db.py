from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass

# NOTE: This cannot go into the type checking block, otherwise SQL runtime error
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterator, Optional

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import NoResultFound  # type: ignore[attr-defined]
from sqlalchemy.orm import (  # type: ignore[attr-defined]
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
)

from elliptio.interfaces import (
    ID,
    AutomaticMetadata,
    DataBaseInterface,
    FileInfo,
    ManualMetadata,
)


class NoDatabaseEntryError(ValueError):
    pass


@dataclass
class SqlDatabase(DataBaseInterface):
    def __init__(self, db_path: Path) -> None:
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
        _Base.metadata.create_all(self.engine)

    def save(self, info: FileInfo) -> None:
        row = _FileRow.from_fileinfo(info)
        with self._get_session() as s:
            s.add(row)
            s.commit()

    def load(self, file_id: ID) -> FileInfo:
        with self._get_session() as s:
            try:
                row: _FileRow = s.query(_FileRow).get(file_id)  # type: ignore[assignment]
            except NoResultFound:
                raise NoDatabaseEntryError from None
            else:
                return row.to_fileinfo()

    def query(self, filter_dict: dict | None, **kwargs) -> pd.DataFrame:
        del kwargs  # we don't need it here, but other adapters might!
        dct = filter_dict or {}
        with self._get_session() as s:
            query = s.query(_FileRow).filter_by(**dct)
            return pd.read_sql(query.statement, query.session.bind)  # type: ignore [arg-type]

    @contextlib.contextmanager
    def _get_session(self) -> Iterator[Session]:
        with Session(self.engine) as s:  # type: ignore[attr-defined]
            yield s


class _Base(DeclarativeBase):
    pass


# NOTE: Can simplify this?! See https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
class _FileRow(_Base, MappedAsDataclass):
    __tablename__ = "files"

    file_id: Mapped[str] = mapped_column(primary_key=True)
    run_id: Mapped[str]
    relpath: Mapped[str]
    remote_url: Mapped[str]
    file_hash: Mapped[str]
    byte_size: Mapped[int]
    deduplicated_by: Mapped[Optional[str]]  # noqa: UP007
    based_on: Mapped[str]

    # automatic metadata
    creation_time: Mapped[datetime]
    argv: Mapped[str]
    username: Mapped[str]
    hostname: Mapped[str]
    python_packages: Mapped[str]

    # manual_metadata
    ticket: Mapped[str]
    project: Mapped[str]
    datatype: Mapped[str]
    dataset: Mapped[str]
    description: Mapped[str]
    config: Mapped[str]

    @classmethod
    def from_fileinfo(cls, info: FileInfo) -> _FileRow:
        amd = info.automatic_metadata
        mmd = info.manual_metadata
        return _FileRow(
            file_id=info.file_id,
            run_id=info.run_id,
            relpath=info.relpath,
            remote_url=info.remote_url,
            file_hash=info.file_hash,
            byte_size=info.byte_size,
            deduplicated_by=info.deduplicated_by,
            based_on=json.dumps(info.based_on),
            # automatic metadata
            creation_time=amd.creation_time.astimezone(None),
            argv=amd.argv,
            username=amd.username,
            hostname=amd.hostname,
            python_packages=json.dumps(amd.python_packages),
            # manual metadata
            ticket=mmd.ticket,
            project=mmd.project,
            datatype=mmd.datatype,
            dataset=mmd.dataset,
            description=mmd.description,
            config=mmd.config,
        )

    def to_fileinfo(self) -> FileInfo:
        amd = AutomaticMetadata(
            creation_time=self.creation_time.astimezone(tz=timezone.utc),
            argv=self.argv,
            username=self.username,
            hostname=self.hostname,
            python_packages=json.loads(self.python_packages),
        )
        mmd = ManualMetadata(
            ticket=self.ticket,
            project=self.project,
            datatype=self.datatype,
            dataset=self.dataset,
            description=self.description,
            config=self.config,
        )
        return FileInfo(
            file_id=ID(self.file_id),
            run_id=ID(self.run_id),
            relpath=self.relpath,
            remote_url=self.remote_url,
            file_hash=self.file_hash,
            byte_size=self.byte_size,
            automatic_metadata=amd,
            manual_metadata=mmd,
            deduplicated_by=_optional_str_to_id(self.deduplicated_by),
            based_on=json.loads(self.based_on),
        )


def _optional_str_to_id(s: str | None) -> ID | None:
    if s is None:
        return None
    return ID(s)
