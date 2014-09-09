"""Utility functions for working with virtualenvs.

(Everything not dependent on Sublime or its API should go here.)
"""

__all__ = ('activate', 'find_virtualenvs', 'is_virtualenv', 'find_pythons')

from functools import lru_cache
from itertools import chain
import logging
import os
import re
import subprocess
import sys


logger = logging.getLogger(__name__)


BINDIR = "bin"
ACTIVATE_SCRIPT = "activate"
if sys.platform == 'win32':
    BINDIR = "Scripts"
    ACTIVATE_SCRIPT += ".bat"

PYTHON_NAME_RE = re.compile(r'python[\d\.]*(?:\.exe)?$')
PYPY_NAME_RE = re.compile(r'pypy[\d\.]*(?:\.exe)?$')


def activate(virtualenv):
    """Return a dict with the changes caused by the virtualenv.

    The changes are:
    - Prepend the path of the virtualenv binary directory to $PATH.
    - Set a $VIRTUAL_ENV variable with the path to the activated virtualenv.
    """
    system_path = os.environ.get('PATH', os.defpath)
    virtualenv_path = os.path.join(virtualenv, BINDIR)  # /path/to/venv/bin
    path = os.pathsep.join((virtualenv_path, system_path))  # PATH=/path/to/venv/bin:$PATH

    env = {'VIRTUAL_ENV': virtualenv}

    return {'path': path, 'env': env}


def find_virtualenvs(paths):
    """Find virtualenvs in the given paths.

    Returns a sorted list with the results.
    """
    virtualenvs = []
    for path in paths:
        if not os.path.isdir(path):
            logger.warning("{} is not a directory. Path ignored.".format(path))
            continue
        subdirs = filter(os.path.isdir, (os.path.join(path, name) for name in os.listdir(path)))
        virtualenvs += sorted(filter(is_virtualenv, subdirs))
    return virtualenvs


def is_virtualenv(path):
    """Test whether 'path' is a virtualenv.

    Assumes that any directory with a "./bin/activate" is a valid virtualenv.
    """
    try:
        return os.path.isfile(os.path.join(path, BINDIR, ACTIVATE_SCRIPT))
    except IOError:
        return False

is_valid = is_virtualenv


@lru_cache()
def find_pythons(paths=(), extra_paths=(), req_modules=()):
    """Find available python binaries.

    Matches a regex against filenames.

    Searches every directory in $PATH by default.
    Extends the search to any additional directory passed in 'extra_paths'.

    Found pythons will be optionally filtered based on the availability of
    modules passed through the 'req_modules' parameter.

    Returns a sorted list with the results.
    """
    paths = paths or os.environ.get('PATH', os.defpath).split(os.pathsep)
    paths = chain(paths, extra_paths)

    is_exec = lambda path: os.path.isfile(path) and os.access(path, os.X_OK)

    found_pythons = []
    for path in filter(os.path.isdir, paths):
        names = os.listdir(path)
        python_names = sorted(filter(PYTHON_NAME_RE.match, names))
        pypy_names = sorted(filter(PYPY_NAME_RE.match, names))
        pythons = list(filter(is_exec, (os.path.join(path, name)
                              for name in python_names + pypy_names)))

        if req_modules:
            # Hide subprocess window in Windows:
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            modules = ", ".join(req_modules)
            for python in pythons[:]:
                cmd = [python, "-c", "import " + modules]
                import_error = subprocess.call(cmd, startupinfo=startupinfo)
                if import_error:
                    pythons.remove(python)

        found_pythons += pythons
    return found_pythons
