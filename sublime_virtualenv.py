
import logging
import os.path
import shlex
import shutil

import sublime
import sublime_plugin
import Default as sublime_default

from . import virtualenv_lib as virtualenv


logger = logging.getLogger(__name__)


def settings():
    return sublime.load_settings("Virtualenv.sublime-settings")


class VirtualenvCommand:

    @property
    def virtualenv_exec(self):
        return shlex.split(settings().get('executable'))

    @property
    def virtualenv_directories(self):
        return [os.path.expanduser(path)
                for path in settings().get('virtualenv_directories')]

    def get_virtualenv(self, **kwargs):
        venv = kwargs.pop('virtualenv', "")

        if not venv:
            project_data = self.window.project_data() or {}
            venv = project_data.get('virtualenv', "")

        return os.path.expanduser(venv)

    def set_virtualenv(self, venv):
        project_data = self.window.project_data() or {}

        if venv:
            project_data['virtualenv'] = venv
            sublime.status_message("({}) ACTIVATED".format(os.path.basename(venv)))
        else:
            try:
                del project_data['virtualenv']
                sublime.status_message("DEACTIVATED")
            except KeyError:
                pass

        self.window.set_project_data(project_data)
        logger.info("Current virtualenv set to \"{}\".".format(venv))

    def find_virtualenvs(self):
        return virtualenv.find_virtualenvs(self.virtualenv_directories)

    def find_pythons(self):
        extra_paths = tuple(settings().get('extra_paths', []))
        return virtualenv.find_pythons(extra_paths=extra_paths)


class VirtualenvWindowCommand(sublime_plugin.WindowCommand, VirtualenvCommand):
    pass


class VirtualenvExecCommand(sublime_default.exec.ExecCommand, VirtualenvCommand):
    def run(self, **kwargs):
        venv = self.get_virtualenv(**kwargs)
        postactivate = virtualenv.activate(venv)
        kwargs['path'] = postactivate['path']
        kwargs['env'] = dict(kwargs.get('env', {}), **postactivate['env'])
        logger.info("Command executed with virtualenv \"{}\".".format(venv))
        super(VirtualenvExecCommand, self).run(**kwargs)


class ActivateVirtualenvCommand(VirtualenvWindowCommand):
    def run(self, **kwargs):
        self.available_venvs = self.find_virtualenvs()
        self.window.show_quick_panel(self.available_venvs, self._set_virtualenv)

    def _set_virtualenv(self, index):
        if index != -1:
            venv = self.available_venvs[index]
            self.set_virtualenv(venv)


class DeactivateVirtualenvCommand(VirtualenvWindowCommand):
    def run(self, **kwargs):
        self.set_virtualenv(None)

    def is_enabled(self):
        return bool(self.get_virtualenv())


class NewVirtualenvCommand(VirtualenvWindowCommand):
    def run(self, **kwargs):
        self.window.show_input_panel(
            "Virtualenv Path:", self.virtualenv_directories[0] + os.path.sep,
            self.get_python, None, None)

    def get_python(self, venv):
        self.venv = os.path.expanduser(os.path.normpath(venv))
        self.found_pythons = self.find_pythons()
        self.window.show_quick_panel(self.found_pythons, self.create_virtualenv)

    def create_virtualenv(self, python_index):
        cmd = self.virtualenv_exec
        if python_index != -1:
            python = self.found_pythons[python_index]
            cmd += ['-p', python]
        cmd += [self.venv]
        self.window.run_command('exec', {'cmd': cmd})
        self.set_virtualenv(self.venv)


class RemoveVirtualenvCommand(VirtualenvWindowCommand):
    def run(self, **kwargs):
        self.available_venvs = self.find_virtualenvs()
        self.window.show_quick_panel(self.available_venvs, self.remove_virtualenv)

    def remove_virtualenv(self, index):
        if index == -1:
            return

        venv = self.available_venvs[index]
        confirmed = sublime.ok_cancel_dialog(
            "Please confirm deletion of virtualenv at \"{}\".".format(venv))
        if confirmed:
            try:
                shutil.rmtree(venv)
                logger.info("\"{}\" deleted.".format(venv))
            except (IOError, OSError):
                logger.error("Could not delete \"{}\".".format(venv))
            else:
                if venv == self.get_virtualenv():
                    self.set_virtualenv(None)
