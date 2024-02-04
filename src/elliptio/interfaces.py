from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime

    import pandas as pd

from dataclasses import dataclass


class ID(str):
    __slots__ = ()


@dataclass
class AutomaticMetadata:
    creation_time: datetime.datetime
    argv: str
    username: str
    hostname: str
    python_packages: dict[str, str]

    # TODO
    # git hash, git diff, ...
    # machine hostname (IP-address?)
    # env-vars (caution: passwords!)


@dataclass
class ManualMetadata:
    ticket: str = ""
    project: str = ""
    datatype: str = ""
    dataset: str = ""
    description: str = ""


@dataclass
class FileInfo:
    run_id: ID
    file_id: ID
    relpath: str
    remote_url: str
    file_hash: str
    byte_size: int
    automatic_metadata: AutomaticMetadata
    manual_metadata: ManualMetadata

    deduplicated_by: ID | None
    based_on: list[ID]


@dataclass
class FileSystemInterface(abc.ABC):
    def define_prefix(self, amd: AutomaticMetadata) -> str:
        return (
            f"{amd.creation_time.year}"
            f"/{amd.creation_time.month}"
            f"/{amd.creation_time.day}"
            f"/{amd.username}"
        )

    def define_remote_url(self, prefix: str, relpath: str) -> str:
        return prefix + "/" + relpath

    @abc.abstractmethod
    def upload(self, local_path: str, remote_url: str) -> None:
        pass

    @abc.abstractmethod
    def download(self, remote_url: str, local_path: str) -> None:
        pass

    @abc.abstractmethod
    def write_text(self, remote_url: str, text: str) -> None:
        pass

    @abc.abstractmethod
    def read_text(self, remote_url: str) -> str:
        pass

    @abc.abstractmethod
    def get_hash(self, remote_url: str) -> str:
        pass

    @abc.abstractmethod
    def get_byte_size(self, remote_url: str) -> int:
        pass


@dataclass
class File(FileInfo):
    fs: FileSystemInterface

    def upload(self, local_path: str) -> None:
        self.fs.upload(local_path, self.remote_url)

    def download(self, local_path: str) -> None:
        self.fs.download(self.remote_url, local_path)

    def write_text(self, text: str) -> None:
        self.fs.write_text(self.remote_url, text)

    def read_text(self) -> str:
        return self.fs.read_text(self.remote_url)

    def update_hash_and_byte_size(self):
        self.file_hash = self.fs.get_hash(self.remote_url)
        self.byte_size = self.fs.get_byte_size(self.remote_url)


@dataclass
class DataBaseInterface(abc.ABC):
    @abc.abstractmethod
    def save(self, info: FileInfo) -> None:
        pass

    @abc.abstractmethod
    def load(self, file_id: ID) -> FileInfo:
        pass

    @abc.abstractmethod
    def query(self, dct: dict, **kwargs) -> pd.DataFrame:
        # The dataframe has columns corresponding to FileInfo
        # TODO: Can we create a new type for this, e.g. DataFrame[FileInfo]?
        pass


class TrackerInterface(abc.ABC):
    @abc.abstractmethod
    def get_automatic_metadata(self) -> AutomaticMetadata:
        pass


class IdCreatorInterface(abc.ABC):
    @abc.abstractmethod
    def create_unique_id(self) -> ID:
        pass
