from __future__ import annotations

import os
import typing
from pathlib import PurePosixPath

import boto3
import dotenv

from elliptio.filetypes import interface

if typing.TYPE_CHECKING:
    from elliptio.metadata import Metadata
import functools
from dataclasses import dataclass
from pathlib import Path

dotenv.load_dotenv()


@functools.lru_cache
def _get_bucket():
    s3 = boto3.resource("s3")
    bucket_name = os.environ["S3_BUCKET_NAME"]
    return s3.Bucket(bucket_name)


@dataclass
class S3File(interface.AbstractFile):
    def upload(self, local_path: Path):
        bucket = _get_bucket()
        bucket.upload_file(
            Filename=local_path,
            Key=str(self.remote_url),
        )

    def download(self, local_path: Path):
        bucket = _get_bucket()
        bucket.download_file(
            Key=str(self.remote_url),
            Filename=local_path,
        )

    def upload_string(self, s: str):
        bucket = _get_bucket()
        obj = bucket.Object(key=str(self.remote_url))
        obj.put(Body=s)

    def download_string(self) -> str:
        bucket = _get_bucket()
        obj = bucket.Object(key=str(self.remote_url))
        response = obj.get()
        return response["Body"].read().decode()

    @classmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        today = metadata.creation_time.strftime("%Y/%m/%d")
        time = metadata.creation_time.strftime("%H%M%S")
        return PurePosixPath(
            f"{today}/{metadata.username}/{time}_{metadata.artifact_id}",
        )
