# ruff: noqa: S105, SLF001
import os
import tempfile
from pathlib import Path, PurePosixPath

import boto3
import elliptio_data_lake as eio
import pytest
from elliptio_data_lake import _save_func
from moto import mock_s3


# TODO: Move to conftest.py
@pytest.fixture(scope="session", autouse=True)
def _aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "test-id"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-key"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["S3_BUCKET_NAME"] = "test-bucket"


@pytest.fixture()
def s3_bucket_name():
    return os.environ["S3_BUCKET_NAME"]


@pytest.fixture()
def mock_base_path(monkeypatch: pytest.MonkeyPatch):
    base_path = PurePosixPath("/test/base/path")
    monkeypatch.setattr(_save_func, "_get_s3_base_path", lambda: base_path)
    return base_path


@pytest.fixture()
def some_local_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        path_a = Path(tmpdir) / "a.txt"
        path_b = Path(tmpdir) / "b/b.md"
        path_a.write_text("a")
        path_b.parent.mkdir()
        path_b.write_text("bb")
        yield [path_a, path_b]


@mock_s3
def test_save_stores_files_in_s3(mock_base_path, some_local_files, s3_bucket_name):
    conn = boto3.resource("s3")
    conn.create_bucket(Bucket=s3_bucket_name)

    eio.save(some_local_files)

    actual_keys = {o.key for o in conn.Bucket(s3_bucket_name).objects.all()}
    expected_keys = {str(mock_base_path / k) for k in ["files/a.txt", "files/b/b.md"]}
    assert actual_keys == expected_keys


def test_get_python_packages():
    packages = _save_func._get_python_packages()

    assert "requests" in packages
