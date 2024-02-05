import hashlib

import fsspec

from elliptio.interfaces import ID, AutomaticMetadata, FileSystemInterface


class FsspecFilesystem(FileSystemInterface):
    def __init__(self, prefix: str, protocol="file", **storage_options) -> None:
        self.fs: fsspec.AbstractFileSystem = fsspec.filesystem(
            protocol,
            **storage_options,
        )
        self.prefix = prefix

    def define_remote_url(
        self,
        amd: AutomaticMetadata,
        file_id: ID,
        relpath: str,
    ) -> str:
        return self.fs.sep.join(
            [
                self.prefix,
                str(amd.creation_time.year),
                str(amd.creation_time.month),
                str(amd.creation_time.day),
                str(amd.username),
                file_id,
                relpath,
            ],
        )

    def create_parent_dir(self, remote_url: str) -> None:
        self.fs.mkdirs(self.fs._parent(remote_url), exist_ok=True)  # noqa: SLF001

    def upload(self, local_path: str, remote_url: str) -> None:
        self.create_parent_dir(remote_url)
        self.fs.put(lpath=local_path, rpath=remote_url)

    def download(self, remote_url: str, local_path: str) -> None:
        self.fs.get(rpath=remote_url, lpath=local_path)

    def write_text(self, remote_url: str, text: str) -> None:
        self.create_parent_dir(remote_url)
        with self.fs.open(remote_url, "w") as f:
            f.write(text)

    def read_text(self, remote_url: str) -> str:
        with self.fs.open(remote_url, "r") as r:
            return r.read()

    def get_hash(self, remote_url: str) -> str:
        hasher = hashlib.sha256()
        with self.fs.open(remote_url, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_byte_size(self, remote_url: str) -> int:
        with self.fs.open(remote_url, "rb") as remote_file:
            remote_file.seek(0, 2)  # Move to the end of the file
            return remote_file.tell()  # Current position (in bytes)
