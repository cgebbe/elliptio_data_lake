import time
from dataclasses import asdict, fields
from datetime import UTC, timedelta
from pathlib import Path

import mongomock
import pandas as pd
import pytest
from assertpy import assert_that, soft_assertions
from elliptio import Handler, Labels, LocalFile


@pytest.fixture()
def local_dirpath(tmp_path):
    Path(tmp_path / "b").mkdir()
    Path(tmp_path / "a.txt").write_text("foo")
    Path(tmp_path / "b/b.md").write_text("bar")
    return tmp_path


@pytest.fixture()
def handler(monkeypatch, tmp_path):
    monkeypatch.setenv("ELLIPTIO_LOCAL_ROOT", tmp_path)
    return Handler(
        remote_file_cls=LocalFile,
        collection=mongomock.MongoClient().db.collection,
    )


def test_upload(handler: Handler, local_dirpath):
    artifact = handler.upload(local_paths=local_dirpath.glob("**/*.*"))
    _check_artifact(artifact)


def test_upload_with_labels(handler: Handler, local_dirpath):
    dct = {f.name: f"my_{f.name}" for f in fields(Labels)}
    artifact = handler.upload(
        local_paths=local_dirpath.glob("**/*.*"),
        labels=Labels(**dct),
    )
    assert_that(asdict(artifact.metadata.labels)).is_equal_to(dct)


def _check_artifact(artifact):
    assert artifact.files["a.txt"].exists()
    assert artifact.files["a.txt"].download_string() == "foo"
    assert artifact.files["b/b.md"].exists()
    assert artifact.files["b/b.md"].download_string() == "bar"


def test_new(handler: Handler):
    with handler.new(relative_paths=["a.txt", "b/b.md"]) as artifact:
        # Creating the directory is only necessary when
        Path(artifact.files["b/b.md"].remote_url).parent.mkdir(
            exist_ok=True,
            parents=True,
        )
        Path(artifact.files["a.txt"].remote_url).write_text("foo")
        Path(artifact.files["b/b.md"].remote_url).write_text("bar")
    _check_artifact(artifact)


def test_find(handler: Handler, local_dirpath):
    handler.upload(local_paths=local_dirpath.glob("**/*.*"))

    df = handler.find(query={})

    print(df)
    assert isinstance(df, pd.DataFrame)


def test_file(handler: Handler, local_dirpath):
    artifact = handler.upload(local_paths=local_dirpath.glob("**/*.md"))
    assert artifact.file.download_string() == "bar"


def test_get(handler: Handler, local_dirpath):
    org = handler.upload(local_paths=local_dirpath.glob("**/*.*"))
    time.sleep(2)

    act = handler.get(artifact_id=org.metadata.artifact_id)

    _compare_metadat_dicts(
        asdict(org.metadata),
        asdict(act.metadata),
    )


def _compare_metadat_dicts(org: dict, act: dict):
    assert org.keys() == act.keys()
    with soft_assertions():
        for k in org:
            if k == "creation_time":
                delta = abs(org[k] - act[k].replace(tzinfo=UTC))
                assert_that(delta).is_less_than(timedelta(seconds=1))
            else:
                assert_that(org[k]).is_equal_to(act[k])
