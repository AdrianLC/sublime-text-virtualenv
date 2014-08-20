
__all__ = ['VIRTUALENV_BINDIR', 'find_pythons']

from functools import lru_cache


VIRTUALENV_BINDIR = "Scripts"


@lru_cache()
def find_pythons(paths):
    pass
