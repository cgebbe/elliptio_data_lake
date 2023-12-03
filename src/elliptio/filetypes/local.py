from __future__ import annotations

import os
import shutil
import typing
from pathlib import Path, PurePosixPath

from elliptio.filetypes import RemoteFileInterface

if typing.TYPE_CHECKING:
    from elliptio.metadata import Metadata


class LocalFile(RemoteFileInterface):
    def exists(self) -> bool:
        return Path(self.remote_url).exists()

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
        today = metadata.creation_time.strftime("%Y/%m/%d")
        time = metadata.creation_time.strftime("%H%M%S")

        artifact_root = (
            PurePosixPath(remote_root)
            / f"{today}/{metadata.username}/{time}_{metadata.artifact_id}"
        )

        # TODO: This is an ugly hack for the LocalFile class, not necessary for S3.
        Path(artifact_root / "files").mkdir(exist_ok=True, parents=True)
        return artifact_root
