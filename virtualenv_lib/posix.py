
__all__ = ['VIRTUALENV_BINDIR', 'find_pythons']

from functools import lru_cache
import logging
import os.path
import re


logger = logging.getLogger(__name__)


VIRTUALENV_BINDIR = "bin"


_python_name_re = re.compile(r'python(?:\d(?:\.\d)?)?$')


@lru_cache()
def find_pythons(paths):
    pythons = []
    for path in paths:
        if not os.path.isdir(path):
            logger.warning("{} is not a directory. Path ignored.".format(path))
            continue
        python_names = filter(_python_name_re.match, os.listdir(path))
        pythons += sorted(filter(os.path.isfile, (os.path.join(path, python)
                          for python in python_names)))
    return pythons
