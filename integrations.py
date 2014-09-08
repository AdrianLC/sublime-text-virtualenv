"""Integrations with other Sublime packages."""

import sublime

from .commands import VirtualenvCommand, InvalidVirtualenv
from . import virtualenv_lib as virtualenv


# SublimeREPL integration:
class CurrentVirtualenvReplCommand(VirtualenvCommand):

    """Launches a Python REPL with the active virtualenv."""

    def run(self, **kwargs):
        """Open the REPL with the virtualenv.

        Based on the original Python + virtualenv REPL:
        https://github.com/wuub/SublimeREPL/blob/master/lang_integration.py#L86
        """
        try:
            venv = self.get_virtualenv(validate=True, **kwargs)
        except InvalidVirtualenv as error:
            sublime.error_message(str(error) + " REPL cancelled!")
            return

        postactivate = virtualenv.activate(venv)

        self.window.run_command('repl_open', {
            'type': 'subprocess',
            'autocomplete_server': True,

            'cmd': ["python", "-u", "${packages}/SublimeREPL/config/Python/ipy_repl.py"],
            'cwd': "$file_path",
            'encoding': 'utf8',
            'extend_env': dict({
                'PATH': postactivate['path'],
                'PYTHONIOENCODING': 'utf-8'
            }, **postactivate['env']),

            'syntax': "Packages/Python/Python.tmLanguage",
            'external_id': "python"
        })

    def is_enabled(self):
        """If SublimeREPL is installed and a virtualenv is active."""
        try:
            import SublimeREPL  # noqa
            return bool(self.get_virtualenv())
        except ImportError:
            return False
