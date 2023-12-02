import abc
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from elliptio.metadata import Metadata


@dataclass
class RemoteFileInterface(abc.ABC):
    remote_url: PurePosixPath

    @abc.abstractmethod
    def upload(self, local_path: Path):
        pass

    @abc.abstractmethod
    def upload_string(self, s: str):
        pass

    @abc.abstractmethod
    def download(self, local_path: Path):
        pass

    @abc.abstractmethod
    def download_string(self) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        pass
