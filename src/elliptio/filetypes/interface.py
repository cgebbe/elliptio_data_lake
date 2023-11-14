import abc
from pathlib import Path, PurePosixPath

from elliptio.metadata import Metadata


class AbstractFile(abc.ABC):
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

    @abc.abstractclassmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        pass
