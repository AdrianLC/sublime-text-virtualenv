
__all__ = ['activate', 'find_virtualenvs', 'is_virtualenv']

import logging
import os
import sys

if sys.platform == 'win32':
    from .windows import *  # noqa
else:
    from .posix import *  # noqa


logger = logging.getLogger(__name__)


def activate(virtualenv):
    return {'path': postactivate_path(virtualenv),
            'env': postactivate_env(virtualenv)}


def postactivate_path(virtualenv):
    current_path = os.environ.get('PATH', "")
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
