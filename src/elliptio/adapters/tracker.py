from elliptio.interfaces import TrackerInterface, AutomaticMetadata
import datetime
import functools
import socket
import getpass
import importlib
import sys


class Tracker(TrackerInterface):
    def get_automatic_metadata(self) -> AutomaticMetadata:
        return AutomaticMetadata(
            run_id="random_id",
            creation_time=datetime.datetime.now(),
            argv=" ".join(sys.orig_argv),
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
    - `pip freeze`: pip is not installed in rye venvs
    - `pkg_resources`: deprecated in favor of importlib.resources or importlib.metadata
    """
    return {d.name: d.version for d in importlib.metadata.distributions()}
