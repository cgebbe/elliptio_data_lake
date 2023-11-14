from __future__ import annotations

import functools
import getpass
import importlib.metadata
import os
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Iterable

import boto3
import yaml
from assertpy import assert_that, soft_assertions


class S3File:
    _bucket = None

    def __init__(self, remote_url: Path) -> None:
        self.remote_url = remote_url
        self._init_class()

    @classmethod
    def _init_class(cls):
        if cls._bucket is not None:
            return
        s3 = boto3.resource("s3")
        bucket_name = os.environ["S3_BUCKET_NAME"]
        cls._bucket = s3.Bucket(bucket_name)

    def upload(self, local_path):
        self._bucket.upload_file(
            Filename=local_path,
            Key=str(self.remote_url),
        )

    def upload_string(self, s: str):
        self._bucket.Object(key=str(self.remote_url)).put(Body=s)

    def download(self, local_path):
        self._bucket.download_file(
            Key=str(self.remote_url),
            Filename=local_path,
        )

    @classmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        today = metadata.creation_time.strftime("%Y/%m/%d")
        time = metadata.creation_time.strftime("%H%M%S")
        return PurePosixPath(
            f"{today}/{metadata.username}/{time}_{metadata.artifact_id}",
        )


@dataclass
class Artifact:
    metadata: Metadata
    files: dict[Path, S3File]
    logs: dict[Path, S3File]


class Handler:
    def __init__(self, file_cls: type[S3File]):
        self.File: type[S3File] = file_cls
        self.run_id = (_get_id(prefix="run_"),)
        # TODO: access collection
        self.collection = None

    def upload(self, local_paths: Iterable[Path]):
        with soft_assertions():
            for i in local_paths:
                assert_that(str(i)).exists().is_file()

        # define metadata
        metadata = _get_metadata(run_id=self.run_id)

        # define local and remote root
        local_abs_paths = [Path(i).resolve() for i in local_paths]
        local_root = os.path.commonprefix(local_abs_paths)
        assert_that(local_root).is_directory()
        remote_root = self.File.define_remote_root(metadata=metadata)

        # TODO: define and upload metadata to database
        yaml_string = yaml.safe_dump(asdict(metadata))
        self.File(remote_root / "metadata.yaml").upload_string(yaml_string)

        # TODO: upload logs
        logs = {}

        # upload files
        files: dict[str, S3File] = {}
        for lap in local_abs_paths:
            relative_path = lap.relative_to(local_root)
            files[str(relative_path)] = self.File(
                remote_url=remote_root / "files" / relative_path,
            )
            files[str(relative_path)].upload(lap)

        return Artifact(
            metadata=metadata,
            files=files,
            logs=logs,
        )


@functools.lru_cache
def _get_username():
    return getpass.getuser()


@dataclass
class Metadata:
    username: str
    argv: str
    artifact_id: str
    run_id: str
    creation_time: datetime.datetime
    python_packages: dict[str, str]


def _get_metadata(run_id: str) -> Metadata:
    return Metadata(
        artifact_id=_get_id(prefix="artifact_"),
        run_id=run_id,
        username=_get_username(),
        argv=" ".join(sys.orig_argv),
        creation_time=datetime.now(tz=UTC),
        python_packages=_get_python_packages(),
    )


def _get_id(prefix: str = ""):
    return f"{prefix}{uuid.uuid4()}"


def _get_python_packages():
    """Gets list of installed python packages.

    Some alternatives:
    - `pip freeze`: pip is not installed in rye venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.name: d.version for d in importlib.metadata.distributions()}
