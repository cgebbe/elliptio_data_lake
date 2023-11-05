from __future__ import annotations

import functools
import getpass
import importlib.metadata
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Iterable

import boto3
import yaml
from assertpy import assert_that, soft_assertions


@dataclass
class File:
    s3_url: PurePosixPath


def save(items: Iterable[os.PathLike]):
    with soft_assertions():
        for i in items:
            assert_that(str(i)).exists().is_file()

    # init bucket handle
    s3 = boto3.resource("s3")
    bucket_name = os.environ["S3_BUCKET_NAME"]
    bucket = s3.Bucket(bucket_name)
    s3_base_path = _get_s3_base_path()

    # add files
    paths = [Path(i).resolve() for i in items]
    common_parent = os.path.commonprefix(paths)
    assert_that(common_parent).is_directory()
    for p in paths:
        bucket.upload_file(
            Filename=str(p),
            Key=str(s3_base_path / "files" / p.relative_to(common_parent)),
        )

    # add metadata
    metadata = _get_metadata()
    metadata["files"] = [str(p.relative_to(common_parent)) for p in paths]
    metadata["s3_base_path"] = str(s3_base_path)
    yaml_string = yaml.safe_dump(metadata)
    s3.Object(
        bucket_name=bucket_name,
        key=str(s3_base_path / "metadata.yaml"),
    ).put(Body=yaml_string)

    return metadata


def _get_s3_base_path():
    now = datetime.now(tz=UTC)
    today = now.strftime("%Y/%m/%d")
    time = now.strftime("%H%M%S")
    unique_id = uuid.uuid4()
    user = _get_username()
    return PurePosixPath(f"{today}/{user}/{time}_{unique_id}")


@functools.lru_cache
def _get_username():
    return getpass.getuser()


def _get_metadata():
    return {
        "user": _get_username(),
        "creation_time": datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S"),
        "python_packages": _get_python_packages(),
    }


def _get_python_packages():
    """Gets list of installed python packages.

    Some alternatives:
    - `pip freeze`: pip is not installed in rye venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.name: d.version for d in importlib.metadata.distributions()}
