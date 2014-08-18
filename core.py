
import logging
import os
import sys


logger = logging.getLogger(__name__)


class Virtualenv:

    BIN_DIR = "Scripts" if sys.platform == 'win32' else "bin"

    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root

    @property
    def name(self):
        return os.path.basename(self.root)

    @property
    def path(self):
        return os.path.join(self.root, self.BIN_DIR)

    @property
    def activated_path(self):
        return os.pathsep.join((self.path, os.environ.get('PATH', "")))  # PATH=/venv/path:$PATH

    @property
    def activated_env(self):
        return {'VIRTUAL_ENV': str(self)}


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
        return os.path.isfile(os.path.join(path, Virtualenv.BIN_DIR, "activate"))
    except IOError:
        return False
