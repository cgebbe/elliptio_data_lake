from elliptio.adapters.fs import FsspecFilesys, FileSystemInterface
from pathlib import Path
import pytest


@pytest.fixture
def fs():
    return FsspecFilesys("local")


@pytest.fixture
def local_path(tmp_path: Path):
    local_path = tmp_path / "local.txt"
    local_path.write_text("foo")
    return str(local_path)


def test_upload_download(fs: FileSystemInterface, tmp_path: Path, local_path: str):
    remote_url = tmp_path / "remote.txt"
    download_path = tmp_path / "downloaded.txt"

    fs.upload(local_path, str(remote_url))
    fs.download(str(remote_url), str(download_path))

    assert download_path.read_text() == Path(local_path).read_text()


def test_write_read_text(fs: FileSystemInterface, tmp_path: Path):
    remote_url = str(tmp_path / "remote.txt")
    text = "foobarbaz"

    fs.write_text(remote_url, text)

    assert fs.read_text(remote_url) == text


def test_hash(fs: FileSystemInterface, local_path: str):
    assert fs.get_hash(local_path) == "acbd18db4cc2f85cedef654fccc4a4d8"


def test_get_byte_size(fs: FileSystemInterface, local_path: str):
    assert fs.get_byte_size(local_path) == 3
