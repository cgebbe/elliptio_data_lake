from __future__ import annotations

import os
import typing
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

import dotenv
import pandas as pd
import pymongo
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
    files: dict[str, AbstractFile]
    logs: dict[str, AbstractFile]


class DocumentNotFoundError(Exception):
    def __init__(self, artifact_id: str) -> None:
        super().__init__(f"Could not find a document with {artifact_id=}.")


class Handler:
    def __init__(self, file_cls: type[AbstractFile]):
        self.File: type[AbstractFile] = file_cls
        self._collection = _get_mongodb_collection()

        self.run_id = get_id(prefix="run_")
        self.based_on: list[str] = []

    def upload(self, local_paths: Iterable[Path]) -> Artifact:
        # TODO: Add fixed labels (ticket, project, dataset, data_type, ...)
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
        metadata.remote_root = str(remote_root)

        # upload files
        files: dict[str, AbstractFile] = {}
        for lap in local_abs_paths:
            relative_path = PurePosixPath(lap.relative_to(local_root))
            remote_url = _get_remote_url(
                remote_root=remote_root,
                relative_path=relative_path,
            )
            files[str(relative_path)] = self.File(remote_url)
            files[str(relative_path)].upload(lap)
        metadata.files = list(files.keys())

        # TODO: upload logs
        logs: dict[str, AbstractFile] = {}
        metadata.logs = list(logs.keys())

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

    def find(
        self,
        query: dict,
        *,
        max_docs: int = 7,
        exclude_columns=("python_packages", "_id"),
    ) -> pd.DataFrame:
        cursor = (
            self._collection.find(
                query,
                projection={c: 0 for c in exclude_columns},
            )
            .sort("creation_time", pymongo.DESCENDING)
            .limit(max_docs)
        )
        dct_list = list(cursor)

        df = pd.DataFrame(dct_list)
        first_columns = [
            "artifact_id",
            "creation_time",
            "username",
            "files",
            "argv",
        ]
        subsequent_columns = set(df.columns).difference(first_columns)
        df = df[first_columns + sorted(subsequent_columns)]
        return df.set_index("artifact_id")

    def get(self, artifact_id: str) -> Artifact:
        doc = self._collection.find_one({"artifact_id": artifact_id})
        if doc is None:
            raise DocumentNotFoundError(artifact_id)

        # NOTE: MongoDB adds _id which we don't use
        doc.pop("_id")
        metadata = Metadata(**doc)

        files = {
            f: self.File(
                _get_remote_url(
                    remote_root=PurePosixPath(metadata.remote_root),
                    relative_path=PurePosixPath(f),
                ),
            )
            for f in metadata.files
        }
        logs = {
            f: self.File(
                _get_remote_url(
                    remote_root=PurePosixPath(metadata.remote_root),
                    relative_path=PurePosixPath(f),
                    is_file=False,
                ),
            )
            for f in metadata.logs
        }
        return Artifact(
            metadata=metadata,
            files=files,
            logs=logs,
        )


def _get_remote_url(
    remote_root: PurePosixPath,
    relative_path: PurePosixPath,
    *,
    is_file: bool = True,
) -> PurePosixPath:
    dirname = "files" if is_file else "logs"
    return remote_root / dirname / relative_path


def _get_mongodb_collection(*, check_connection: bool = True):
    uri = os.environ["MONGODB_FULL_URI"]
    db_name = os.environ["MONGODB_DB_NAME"]
    collection_name = os.environ["MONGODB_COLLECTION_NAME"]
    client: MongoClient = MongoClient(uri)
    if check_connection:
        client.admin.command("ping")
    return client[db_name][collection_name]
