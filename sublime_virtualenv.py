
import os.path

import sublime
import sublime_plugin

from .virtualenv import Virtualenv, find_virtualenvs


def settings():
    return sublime.load_settings("SublimeVirtualenv.sublime-settings")


class VirtualenvCommand:

    @property
    def virtualenv_exec(self):
        return settings().get('virtualenv_executable')

    @property
    def virtualenv_directories(self):
        return [os.path.expanduser(path)
                for path in settings().get('virtualenv_directories')]

    def get_virtualenv(self, **kwargs):
        venv_path = kwargs.pop('virtualenv', "")

        if not venv_path:
            try:
                project_data = self.window.project_data() or {}
                venv_path = project_data['virtualenv']
            except KeyError:
                sublime.error_message("Could not determine virtualenv from settings.")

        venv_path = os.path.expanduser(venv_path)
        virtualenv = Virtualenv(venv_path)
        return virtualenv

    def set_virtualenv(self, virtualenv):
        project_data = self.window.project_data() or {}
        project_data['virtualenv'] = str(virtualenv)
        self.window.set_project_data(project_data)


class RunOnVirtualenvCommand(sublime_plugin.WindowCommand, VirtualenvCommand):
    def run(self, **kwargs):
        virtualenv = self.get_virtualenv(**kwargs)
        kwargs['path'] = virtualenv.activated_path
        kwargs['env'] = dict(kwargs.get('env', {}), **virtualenv.activated_env)
        self.window.run_command('exec', kwargs)  # built-in build command


class ChooseVirtualenvCommand(sublime_plugin.WindowCommand, VirtualenvCommand):
    def run(self, **kwargs):
        self.available_venvs = find_virtualenvs(self.virtualenv_directories)
        self.window.show_quick_panel(self.available_venvs, self._set_virtualenv)

    def _set_virtualenv(self, index):
        if index != -1:
            self.set_virtualenv(self.available_venvs[index])


class NewVirtualenvCommand(sublime_plugin.WindowCommand, VirtualenvCommand):
    def run(self, path="", **kwargs):
        if path:
            self.create_virtualenv(os.path.expanduser(path))
        else:
            self.window.show_input_panel(
                "Virtualenv Path:", self.virtualenv_directories[0] + os.path.sep,
                self.create_virtualenv, None, None)

    def create_virtualenv(self, path):
        virtualenv = Virtualenv(os.path.normpath(path))
        self.window.run_command('exec', {'cmd': [self.virtualenv_exec, virtualenv.root]})
        self.set_virtualenv(virtualenv)
