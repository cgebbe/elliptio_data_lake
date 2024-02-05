from datetime import datetime, timezone
from pathlib import Path

import pytest

from elliptio.adapters.db import SqlDatabase
from elliptio.interfaces import AutomaticMetadata, FileInfo, ManualMetadata


def test_db(file_info: FileInfo, tmp_path: Path):
    db = SqlDatabase(tmp_path / "db.sqlite")

    db.save(file_info)
    reloaded = db.load(file_info.file_id)
    assert reloaded == file_info

    df = db.query({"username": "username"})
    assert len(df) == 1


@pytest.fixture()
def file_info():
    amd = AutomaticMetadata(
        creation_time=datetime.now(tz=timezone.utc),
        argv="argv",
        username="username",
        hostname="hostname",
        python_packages={"a": "1.2", "b": "1.2.3"},
    )
    mmd = ManualMetadata(
        ticket="ticket",
        project="project",
        datatype="datatype",
        dataset="dataset",
        description="description",
        config="config",
    )
    return FileInfo(
        file_id="file_id",
        run_id="run_id",
        relpath="relpath",
        remote_url="remote_url",
        file_hash="file_hash",
        byte_size=123,
        automatic_metadata=amd,
        manual_metadata=mmd,
        deduplicated_by="deduplicated_by",
        based_on=["one", "two", "three"],
    )
