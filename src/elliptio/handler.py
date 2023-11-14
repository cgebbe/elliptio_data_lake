from __future__ import annotations

import os
import typing
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import dotenv
import yaml
from assertpy import assert_that, soft_assertions
from pymongo.mongo_client import MongoClient

if typing.TYPE_CHECKING:
    from elliptio.filetypes import AbstractFile
from elliptio.metadata import Metadata, get_id, get_metadata

dotenv.load_dotenv()


@dataclass
class Artifact:
    metadata: Metadata
    files: dict[Path, AbstractFile]
    logs: dict[Path, AbstractFile]


class Handler:
    def __init__(self, file_cls: type[AbstractFile]):
        self.File: type[AbstractFile] = file_cls
        self.run_id = (get_id(prefix="run_"),)

        # TODO: access collection
        self._collection = _get_mongodb_collection()

    def upload(self, local_paths: Iterable[Path]):
        with soft_assertions():
            for i in local_paths:
                assert_that(str(i)).exists().is_file()

        # define metadata
        metadata = get_metadata(run_id=self.run_id)

        # define local and remote root
        local_abs_paths = [Path(i).resolve() for i in local_paths]
        local_root = os.path.commonprefix(local_abs_paths)
        assert_that(local_root).is_directory()
        remote_root = self.File.define_remote_root(metadata=metadata)

        # upload files
        files: dict[str, AbstractFile] = {}
        for lap in local_abs_paths:
            relative_path = lap.relative_to(local_root)
            files[str(relative_path)] = self.File(
                remote_url=remote_root / "files" / relative_path,
            )
            files[str(relative_path)].upload(lap)

        # TODO: upload logs
        logs = {}

        # upload and insert metadata
        metadata_dict = asdict(metadata)
        yaml_string = yaml.safe_dump(metadata_dict)
        self.File(remote_root / "metadata.yaml").upload_string(yaml_string)
        self._collection.insert_one(metadata_dict)

        return Artifact(
            metadata=metadata,
            files=files,
            logs=logs,
        )


def _get_mongodb_collection(*, check_connection: bool = True):
    uri = os.environ["MONGODB_FULL_URI"]
    db_name = os.environ["MONGODB_DB_NAME"]
    collection_name = os.environ["MONGODB_COLLECTION_NAME"]
    client = MongoClient(uri)
    if check_connection:
        client.admin.command("ping")
    return client[db_name][collection_name]
