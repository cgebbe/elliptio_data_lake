import dataclasses
from pathlib import Path

import pandas as pd
import pytest

from elliptio.composite import Handler, get_default_handler


def test_create_text(handler: Handler):
    with handler.create("my/train.txt") as f:
        f.write_text("foo")

    assert f.read_text() == "foo"


def test_metadata_file_exists(handler: Handler):
    with handler.create("my/train.txt") as f:
        f.write_text("foo")

    metadata_path = handler.fs.define_remote_url(
        f.automatic_metadata,
        f.file_id,
        ".metadata.yaml",
    )
    assert Path(metadata_path).exists()


def test_create_file(handler: Handler, local_path: Path, tmp_path: Path):
    with handler.create("my/train.txt") as f:
        f.upload(str(local_path))

    download_path = tmp_path / "download.txt"
    f.download(str(download_path))
    assert download_path.read_text() == "foo"


def test_load(handler: Handler):
    with handler.create("my/train.txt") as f:
        f.write_text("foo")

    reloaded = handler.load(f.file_id)
    assert dataclasses.asdict(reloaded) == dataclasses.asdict(f)


def test_query(handler: Handler):
    with handler.create("my/train.txt") as f:
        f.write_text("foo")

    df1 = handler.query()
    df2 = handler.query({"relpath": "my/train.txt"})
    assert len(df1) == 1
    pd.testing.assert_frame_equal(df1, df2)


@pytest.fixture()
def handler(tmp_path) -> Handler:
    return get_default_handler(tmp_path)


@pytest.fixture()
def local_path(tmp_path: Path):
    local_path = tmp_path / "composite_test.txt"
    local_path.write_text("foo")
    return str(local_path)
