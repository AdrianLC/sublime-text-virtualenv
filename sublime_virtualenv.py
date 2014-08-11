
import os.path

import sublime
import sublime_plugin

from .virtualenv import Virtualenv


def settings():
    return sublime.load_settings("SublimeVirtualenv.sublime-settings")


class RunOnVirtualenvCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        virtualenv = kwargs.pop('virtualenv',  self.get_virtualenv_from_settings())
        virtualenv = Virtualenv(os.path.expanduser(virtualenv))
        kwargs['path'] = virtualenv.activated_path
        kwargs['env'] = dict(kwargs.get('env', {}), **virtualenv.activated_env)
        self.window.run_command('exec', kwargs)  # built-in build command

    def get_virtualenv_from_settings(self):
        project_settings = self.window.project_data() or {}
        try:
            return project_settings['virtualenv']
        except KeyError:
            sublime.error_message("Could not determine virtualenv from settings.")
