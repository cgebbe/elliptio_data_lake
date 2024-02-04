from datetime import datetime
import functools
import getpass
import importlib.metadata
import socket
import sys


from elliptio.interfaces import AutomaticMetadata, TrackerInterface


class Tracker(TrackerInterface):
    def get_automatic_metadata(self) -> AutomaticMetadata:
        return AutomaticMetadata(
            run_id="random_id",
            creation_time=datetime.utcnow(),
            argv=" ".join(sys.argv),  # NOTE: before sys.orig_argv using 3.11 ?!
            username=_get_username(),
            hostname=_get_hostname(),
            python_packages=_get_python_packages(),
        )


@functools.lru_cache
def _get_hostname():
    return socket.gethostname()


@functools.lru_cache
def _get_username():
    return getpass.getuser()


def _get_python_packages():
    """Gets list of installed python packages.

    Some alternatives:
    - `pip freeze`: pip is not installed in rye or pdm venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.metadata["name"]: d.version for d in importlib.metadata.distributions()}
