import os
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from assertpy import assert_that

from elliptio.filetypes import AbstractFile
from elliptio.metadata import Metadata


@dataclass
class LocalFile(AbstractFile):
    remote_url: PurePosixPath

    def upload(self, local_path: Path):
        Path(self.remote_url).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            src=local_path,
            dst=self.remote_url,
        )

    def download(self, local_path: Path):
        shutil.copy2(
            src=self.remote_url,
            dst=local_path,
        )

    def upload_string(self, s: str):
        Path(self.remote_url).parent.mkdir(parents=True, exist_ok=True)
        Path(self.remote_url).write_text(s, encoding="utf8")

    def download_string(self) -> str:
        return Path(self.remote_url).read_text(encoding="utf8")

    @classmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        remote_root = os.environ["ELLIPTIO_LOCAL_ROOT"]
        assert_that(remote_root).exists().is_directory()

        today = metadata.creation_time.strftime("%Y/%m/%d")
        time = metadata.creation_time.strftime("%H%M%S")
        return (
            PurePosixPath(remote_root)
            / f"{today}/{metadata.username}/{time}_{metadata.artifact_id}"
        )
