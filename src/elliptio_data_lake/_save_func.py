from typing import Iterable
from pathlib import Path, PurePosixPath
import importlib.metadata
import os
import boto3
from assertpy import assert_that, soft_assertions
from datetime import datetime
import uuid
import getpass


def _get_bucket():
    r = boto3.resource("s3")
    return r.Bucket(os.environ["S3_BUCKET_NAME"])


def _get_s3_base_path():
    today = datetime.now().strftime("%Y/%m/%d")
    unique_id = uuid.uuid4()
    user = getpass.getuser()
    return PurePosixPath(f"{today}/{user}/{unique_id}")


def save(items: Iterable[os.PathLike]):
    paths = [Path(i) for i in items]
    with soft_assertions():
        for p in paths:
            assert_that(p).is_file

    bucket = _get_bucket()
    s3_base_path = _get_s3_base_path()
    
    # add files
    paths = [p.resolve() for p in paths]
    common_parent = os.path.commonprefix(paths)
    assert_that(common_parent).is_directory()
    for p in paths:
        bucket.upload_file(
            Filename=str(p),
            Key=str(s3_base_path / "files" / p.relative_to(common_parent)),
        )

    # TODO: add some logs (e.g. git diff, conda env, etc.)

    # TODO: add metadata.yaml at the end with user, git-hash, python packages, etc.



def _get_metadata():
    pass


def _create_git_diff():
    # TODO: Get all files, then diff against current commit and last origin one
    # https://stackoverflow.com/a/35484355
    # repo.git.ls_files(others=True, exclude_standard=True).splitlines()
    pass

def _get_python_packages():
    """Gets list of installed python packages.

    Some alternatives:
    - `pip freeze`: pip is not installed in rye venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.name: d.version for d in importlib.metadata.distributions()}
