
import os

class Virtualenv:

    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root

    @property
    def name(self):
        return os.path.basename(self.root)

    @property
    def path(self):
        return os.path.join(self.root, "bin")

    @property
    def activated_path(self):
        return os.pathsep.join((self.path, os.environ.get('PATH', "")))  # PATH=/venv/path:$PATH

    @property
    def activated_env(self):
        return {'VIRTUAL_ENV': str(self)}
