from __future__ import annotations

import functools
import getpass
import importlib.metadata
import socket
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable

import dotenv

dotenv.load_dotenv()


@dataclass
class Metadata:
    username: str
    hostname: str
    argv: str
    artifact_id: str
    run_id: str
    creation_time: datetime
    python_packages: dict[str, str]

    # TODO
    # git hash, git diff, ...
    # machine hostname (IP-address?)
    # env-vars (optional due to passwords!)

    # TO BE FILLED LATER
    based_on: Iterable[str] = ()
    remote_root: str = ""
    local_root: str = ""
    file_relpaths: Iterable[str] = ()
    log_relpaths: Iterable[str] = ()

    # Likely useful for loading different metadata versions later on
    version: int = 1


def get_metadata(run_id: str) -> Metadata:
    return Metadata(
        artifact_id=get_id(prefix="artifact_"),
        run_id=run_id,
        username=_get_username(),
        hostname=_get_hostname(),
        argv=" ".join(sys.orig_argv),
        creation_time=datetime.now(tz=UTC),
        python_packages=_get_python_packages(),
    )


def get_id(prefix: str = ""):
    return f"{prefix}{uuid.uuid4()}"


@functools.lru_cache
def _get_hostname():
    return socket.gethostname()


@functools.lru_cache
def _get_username():
    return getpass.getuser()


def _get_python_packages():
    """Gets list of installed python packages.

    Some alternatives:
    - `pip freeze`: pip is not installed in rye venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.name: d.version for d in importlib.metadata.distributions()}
