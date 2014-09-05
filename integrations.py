"""Integrations with other Sublime packages."""

import sublime

from .commands import VirtualenvCommand
from . import virtualenv_lib as virtualenv


# SublimeREPL integration:
class CurrentVirtualenvReplCommand(VirtualenvCommand):

    """Launches a Python REPL with the active virtualenv."""

    def run(self, **kwargs):
        """Open the REPL with the virtualenv.

        Based on the original Python + virtualenv REPL:
        https://github.com/wuub/SublimeREPL/blob/master/lang_integration.py#L86
        """
        venv = self.get_virtualenv(**kwargs)

        if not virtualenv.is_valid(venv):
            self.set_virtualenv(None)
            sublime.error_message(
                "Activated virtualenv at \"{}\" is corrupt or has been deleted. REPL cancelled!\n"
                "Choose another virtualenv and launch the REPL again.".format(venv)
            )
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
