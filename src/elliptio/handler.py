from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Iterable, Iterator

import dotenv
import pandas as pd
import pymongo.collection
import toolz
import yaml
from assertpy import assert_that, soft_assertions
from pymongo.mongo_client import MongoClient

if TYPE_CHECKING:
    from elliptio.filetypes import RemoteFileInterface
from elliptio.metadata import Labels, Metadata, get_id, get_metadata

dotenv.load_dotenv()


_LOGGER = logging.getLogger(__name__)


class DocumentNotFoundError(Exception):
    def __init__(self, artifact_id: str) -> None:
        super().__init__(f"Could not find a document with {artifact_id=}.")


@dataclass
class Artifact:
    metadata: Metadata
    files: dict[str, RemoteFileInterface]
    logs: dict[str, RemoteFileInterface]

    @property
    def file(self) -> RemoteFileInterface:
        file_count = len(self.files)
        if file_count != 1:
            msg = f".file() only works if artifact has {file_count=} of 1."
            raise KeyError(msg)
        return toolz.first(self.files.values())

    @classmethod
    def from_metadata(
        cls,
        remote_file_cls: type[RemoteFileInterface],
        metadata: Metadata,
    ):
        files = {
            relpath: remote_file_cls(
                _get_remote_url(
                    remote_root=PurePosixPath(metadata.remote_root),
                    relative_path=PurePosixPath(relpath),
                    dirname="files",
                ),
            )
            for relpath in metadata.file_relpaths
        }
        logs = {
            relpath: remote_file_cls(
                _get_remote_url(
                    remote_root=PurePosixPath(metadata.remote_root),
                    relative_path=PurePosixPath(relpath),
                    dirname="logs",
                ),
            )
            for relpath in metadata.log_relpaths
        }
        return Artifact(
            metadata=metadata,
            files=files,
            logs=logs,
        )


class Handler:
    def __init__(
        self,
        remote_file_cls: type[RemoteFileInterface],
        collection: pymongo.collection.Collection | None = None,
    ):
        self.Remote_File: type[RemoteFileInterface] = remote_file_cls
        self._collection = (
            collection if collection is not None else _get_mongodb_collection()
        )

        self.run_id = get_id(prefix="run_")
        self.based_on: list[str] = []

    def upload(
        self,
        local_paths: Iterable[Path],
        labels: Labels | None = None,
    ) -> Artifact:
        # Problem: If local_paths is generator (like Path().glob()), we exhaust it.
        # Solution: Convert it to a list.
        local_paths = list(local_paths)
        metadata = self._create_metadata(
            relative_paths=_convert_to_relative_paths(local_paths=local_paths),
            labels=labels,
        )

        with soft_assertions():
            for p in local_paths:
                assert_that(str(p)).exists().is_file()

        for relpath, p in zip(metadata.file_relpaths, local_paths):
            remote_url = _get_remote_url(
                remote_root=metadata.remote_root,
                relative_path=relpath,
                dirname="files",
            )
            self.Remote_File(remote_url=remote_url).upload(p)

        self._insert_metadata(metadata)
        return self._create_artifact(metadata)

    def _create_metadata(
        self,
        relative_paths: list[str],
        labels: Labels | None,
    ) -> Metadata:
        metadata = get_metadata(run_id=self.run_id)
        metadata.labels = labels if labels is not None else Labels()
        metadata.based_on = self.based_on.copy()
        metadata.remote_root = str(
            self.Remote_File.define_remote_root(metadata=metadata),
        )
        metadata.file_relpaths = relative_paths
        # TODO: create and upload log files
        return metadata

    def _insert_metadata(self, metadata: Metadata):
        metadata_dict = asdict(metadata)
        _LOGGER.debug(f"Uploading and inserting {metadata_dict=}")
        yaml_string = yaml.safe_dump(metadata_dict)
        self.Remote_File(
            PurePosixPath(metadata.remote_root) / "metadata.yaml",
        ).upload_string(
            yaml_string,
        )
        self._collection.insert_one(metadata_dict)

    def _create_artifact(self, metadata: Metadata):
        return Artifact.from_metadata(
            remote_file_cls=self.Remote_File,
            metadata=metadata,
        )

    @contextmanager
    def new(
        self,
        relative_paths: list[str],
        labels: Labels | None = None,
    ) -> Iterator[Artifact]:
        metadata = self._create_metadata(
            relative_paths=relative_paths,
            labels=labels,
        )
        yield self._create_artifact(metadata)
        # TODO: check that remote files are created ?!
        self._insert_metadata(metadata)

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
            "file_relpaths",
            "argv",
        ]
        assert_that(first_columns).is_subset_of(df.columns)
        subsequent_columns = set(df.columns).difference(first_columns)
        df = df[first_columns + sorted(subsequent_columns)]
        return df.set_index("artifact_id")

    def get(self, artifact_id: str) -> Artifact:
        doc = self._collection.find_one({"artifact_id": artifact_id})
        if doc is None:
            raise DocumentNotFoundError(artifact_id)
        self.based_on.append(artifact_id)

        # NOTE: MongoDB adds _id which we don't use
        doc.pop("_id")
        metadata = Metadata(**doc)
        return Artifact.from_metadata(
            remote_file_cls=self.Remote_File,
            metadata=metadata,
        )


def _convert_to_relative_paths(local_paths: Iterable[Path]) -> list[str]:
    local_abs_paths = [Path(i).resolve() for i in local_paths]
    local_root = os.path.commonprefix([p.parent for p in local_abs_paths])
    assert_that(local_root).is_directory()

    return [str(p.relative_to(local_root)) for p in local_abs_paths]


def _get_remote_url(
    remote_root: str | PurePosixPath,
    relative_path: str | PurePosixPath,
    dirname: str,
) -> PurePosixPath:
    assert_that(dirname).is_in("files", "logs")
    return PurePosixPath(remote_root) / dirname / relative_path


def _get_mongodb_collection(*, check_connection: bool = True):
    uri = os.environ["MONGODB_FULL_URI"]
    client: MongoClient = MongoClient(uri)
    if check_connection:
        client.admin.command("ping")

    db_name = os.environ["MONGODB_DB_NAME"]
    collection_name = os.environ["MONGODB_COLLECTION_NAME"]
    return client[db_name][collection_name]
