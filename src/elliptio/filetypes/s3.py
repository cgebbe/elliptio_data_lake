from __future__ import annotations

import os
import typing
from pathlib import Path, PurePosixPath

import boto3
import dotenv

from elliptio.filetypes import interface

if typing.TYPE_CHECKING:
    from elliptio.metadata import Metadata

dotenv.load_dotenv()


class S3File(interface.AbstractFile):
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

    def download(self, local_path):
        self._bucket.download_file(
            Key=str(self.remote_url),
            Filename=local_path,
        )

    def upload_string(self, s: str):
        obj = self._bucket.Object(key=str(self.remote_url))
        obj.put(Body=s)

    def download_string(self) -> str:
        obj = self._bucket.Object(key=str(self.remote_url))
        response = obj.get()
        return response["Body"].read().decode()

    @classmethod
    def define_remote_root(cls, metadata: Metadata) -> PurePosixPath:
        today = metadata.creation_time.strftime("%Y/%m/%d")
        time = metadata.creation_time.strftime("%H%M%S")
        return PurePosixPath(
            f"{today}/{metadata.username}/{time}_{metadata.artifact_id}",
        )
