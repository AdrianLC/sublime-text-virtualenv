
__all__ = ['activate', 'find_virtualenvs', 'is_virtualenv', 'find_pythons']

from functools import lru_cache
from itertools import chain
import logging
import os
import re
import sys


logger = logging.getLogger(__name__)


VIRTUALENV_BINDIR = "Scripts" if sys.platform == 'win32' else "bin"

PYTHON_NAME_RE = re.compile(r'python[\d\.]*(?:\.exe)?$')


def activate(virtualenv):
    return {'path': postactivate_path(virtualenv),
            'env': postactivate_env(virtualenv)}


def postactivate_path(virtualenv):
    current_path = os.environ.get('PATH', os.defpath)
    virtualenv_path = os.path.join(virtualenv, VIRTUALENV_BINDIR)  # /path/to/venv/bin
    return os.pathsep.join((virtualenv_path, current_path))  # PATH=/path/to/venv/bin:$PATH


def postactivate_env(virtualenv):
    return {'VIRTUAL_ENV': virtualenv}


def find_virtualenvs(paths):
    virtualenvs = []
    for path in paths:
        if not os.path.isdir(path):
            logger.warning("{} is not a directory. Path ignored.".format(path))
            continue
        subdirs = filter(os.path.isdir, (os.path.join(path, name) for name in os.listdir(path)))
        virtualenvs += sorted(filter(is_virtualenv, subdirs))
    return virtualenvs


def is_virtualenv(path):
    try:
        return os.path.isfile(os.path.join(path, VIRTUALENV_BINDIR, "activate"))
    except IOError:
        return False

is_valid = is_virtualenv


@lru_cache()
def find_pythons(paths=(), extra_paths=()):
    paths = chain(paths or os.environ.get('PATH', os.defpath).split(os.pathsep), extra_paths)
    pythons = []
    for path in filter(os.path.isdir, paths):
        python_names = filter(PYTHON_NAME_RE.match, os.listdir(path))
        pythons += sorted(filter(os.path.isfile, (os.path.join(path, python)
                          for python in python_names)))
    return pythons
