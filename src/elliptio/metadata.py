from __future__ import annotations

import functools
import getpass
import importlib.metadata
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import dotenv

dotenv.load_dotenv()


@dataclass
class Metadata:
    username: str
    argv: str
    artifact_id: str
    run_id: str
    creation_time: datetime
    python_packages: dict[str, str]
    # TODO
    # git hash, git diff, ...


def get_metadata(run_id: str) -> Metadata:
    return Metadata(
        artifact_id=get_id(prefix="artifact_"),
        run_id=run_id,
        username=_get_username(),
        argv=" ".join(sys.orig_argv),
        creation_time=datetime.now(tz=UTC),
        python_packages=_get_python_packages(),
    )


def get_id(prefix: str = ""):
    return f"{prefix}{uuid.uuid4()}"


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
