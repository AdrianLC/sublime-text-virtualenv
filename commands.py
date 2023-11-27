"""Sublime Text commands for virtualenv management."""

import logging
import os.path
import shlex
import shutil
import sys

import sublime
import sublime_plugin
import Default as sublime_default

from . import virtualenv_lib as virtualenv


logger = logging.getLogger(__name__)


SETTINGS = "Virtualenv.sublime-settings"


def settings():
    """Return the settings of the plugin."""
    return sublime.load_settings(SETTINGS)


def save_settings():
    """Save plugin settings to disk."""
    sublime.save_settings(SETTINGS)
settings.save = save_settings


class InvalidVirtualenv(Exception):

    """Exception raised when the current virtualenv is missing or corrupt."""

    def __init__(self, venv):
        """Construct automatic error message from virtualenv path."""
        message = (
            "Virtualenv at \"{}\" is missing, corrupt or has been deleted.".format(venv))
        super(InvalidVirtualenv, self).__init__(message)
        self.message = message


class VirtualenvCommand(sublime_plugin.WindowCommand):

    """Base command with virtualenv management functionality."""

    @property
    def virtualenv_exec(self):
        """Virtualenv executable as specified in the settings.

        Returns a list with the command split by shlex.split().
        """
        return shlex.split(settings().get('executable'))

    @property
    def virtualenv_directories(self):
        """The list of directory paths specified in the settings."""
        return [os.path.expanduser(path)
                for path in settings().get('virtualenv_directories')]

    def get_virtualenv(self, validate=False, **kwargs):
        """Get current virtualenv from project data.

        (It will work even if the project has not been saved.
        The data is stored internally anyway.)

        Takes an optional flag 'validate'. If True, the virtualenv
        will be checked and if the validation fails 'InvalidVirtualenv'
        is raised.
        """
        venv = kwargs.pop('virtualenv', "")
        if not venv:
            project_data = self.window.project_data() or {}
            venv = project_data.get('virtualenv', "")
        venv = os.path.expanduser(venv)

        if validate and venv and not virtualenv.is_valid(venv):
            self.set_virtualenv(None)
            raise InvalidVirtualenv(venv)

        return venv

    def set_virtualenv(self, venv):
        """Update the current virtualenv in project data.

        If the passed venv in None, remove virtualenv data from project.
        """
        project_data = self.window.project_data() or {}

        if venv:
            project_data['virtualenv'] = venv
            pyn = os.path.join(venv, 'Scripts', 'Python')
            if not project_data.get('settings', None):
                print('settings added for virtualenv')
                project_data['settings'] = {'python_interpreter': pyn}
            else:
                print('virtualenv added to settings')
                project_data['settings']['python_interpreter'] = pyn
            sublime.status_message("({}) ACTIVATED".format(os.path.basename(venv)))
        else:
            try:
                del project_data['virtualenv']
                del project_data['settings']['python_interpreter']
                sublime.status_message("DEACTIVATED")
            except KeyError:
                pass

        self.window.set_project_data(project_data)
        logger.info("Current virtualenv set to \"{}\".".format(venv))

    def find_virtualenvs(self):
        """Return a list of (basename, path) tuples of the found virtualenvs.

        Searches in open folders and paths defined in the settings.

        The result is valid as input for Sublime's quick panel.
        """
        search_dirs = self.window.folders() + self.virtualenv_directories
        venvs = virtualenv.find_virtualenvs(search_dirs)
        return [[os.path.basename(venv), venv] for venv in venvs]

    def find_pythons(self):
        """Find python executables in the system.

        Searches in os.environ and additional directories defined
        in the settings.
        """
        extra_paths = tuple(settings().get('extra_paths', []))
        return virtualenv.find_pythons(extra_paths=extra_paths)


class VirtualenvExecCommand(sublime_default.exec.ExecCommand, VirtualenvCommand):

    """Extends the default exec command adapting the build parameters."""

    def run(self, **kwargs):
        """Exec the command with virtualenv.

        If a virtualenv is active and valid update the build parameters
        as needed and call the built-in command.

        Else, if no virtualenv is active, do nothing and call the built-in
        command.

        Else, if the active virtualenv is invalid or corrupt display an error
        message and cancel execution.
        """
        try:
            venv = self.get_virtualenv(validate=True, **kwargs)
        except InvalidVirtualenv as error:
            sublime.error_message(str(error) + " Execution cancelled!")
        else:
            if venv:
                kwargs = self.update_exec_kwargs(venv, **kwargs)
                logger.info("Command executed with virtualenv \"{}\".".format(venv))
            super(VirtualenvExecCommand, self).run(**kwargs)

    def update_exec_kwargs(self, venv, **kwargs):
        """Modify exec kwargs to make use of the virtualenv."""
        postactivate = virtualenv.activate(venv)
        kwargs['path'] = postactivate['path']
        kwargs['env'] = dict(kwargs.get('env', {}), **postactivate['env'])
        kwargs['env'].pop('PYTHONHOME', None)
        # On OS X, avoid being run in a login shell, to preserve the virtualenv-ized PATH
        if sys.platform == 'darwin' and 'shell_cmd' in kwargs:
            kwargs['cmd'] = ['/bin/bash', '-c', kwargs['shell_cmd']]
            del kwargs['shell_cmd']
        return kwargs


class ActivateVirtualenvCommand(VirtualenvCommand):

    """Command for selecting active virtualenv."""

    def run(self, **kwargs):
        """Display available virtualenvs in quick panel."""
        self.available_venvs = self.find_virtualenvs()
        self.window.show_quick_panel(self.available_venvs, self._set_virtualenv)

    def _set_virtualenv(self, index):
        if index != -1:
            venv = self.available_venvs[index][1]
            self.set_virtualenv(venv)


class DeactivateVirtualenvCommand(VirtualenvCommand):

    """"Commmand for deactivating the virtualenv."""

    def run(self, **kwargs):
        """Just delete the virtualenv entry from project data."""
        self.set_virtualenv(None)

    def is_enabled(self):
        """Only if the virtualenv entry is set."""
        return bool(self.get_virtualenv())


class NewVirtualenvCommand(VirtualenvCommand):

    """Command for creating a new virtualenv."""

    def run(self, **kwargs):
        """Show input panel requesting virtualenv destination."""
        self.window.show_input_panel(
            "Virtualenv Path:", self.virtualenv_directories[0] + os.path.sep,
            self.get_python, None, None)

    def get_python(self, venv):
        """Show available python binaries in quick panel.

        Callback called with virtualenv destination.
        """
        if not venv:
            return

        self.venv = os.path.expanduser(os.path.normpath(venv))
        self.found_pythons = self.find_pythons()
        self.window.show_quick_panel(self.found_pythons, self.create_virtualenv)

    def create_virtualenv(self, python_index):
        """Execute the command and create the virtualenv.

        Callback called with selected python.

        Constructs the appropriate command with the virtualenv command,
        the selected python and the destination.

        Delegates command execution to the built-in exec command, so
        the process can be killed.

        It will also activate the created virtualenv.
        """
        cmd = self.virtualenv_exec
        if python_index != -1:
            python = self.found_pythons[python_index]
            cmd += ['-p', python]
        cmd += [self.venv]
        self.window.run_command('exec', {'cmd': cmd})
        self.set_virtualenv(self.venv)


class NewBuiltinVirtualenvCommand(NewVirtualenvCommand):

    """Command for creating a new virtualenv with built-in venv module."""

    def find_pythons(self):
        """With venv module available."""
        extra_paths = tuple(settings().get('extra_paths', []))
        return virtualenv.find_pythons(
            extra_paths=extra_paths, req_modules=('venv', ))

    def create_virtualenv(self, python_index):
        """With the venv module installed in the selected python."""
        if python_index == -1:
            return

        python = self.found_pythons[python_index]
        cmd = [python, "-m", "venv", self.venv]
        self.window.run_command('exec', {'cmd': cmd})
        self.set_virtualenv(self.venv)


class RemoveVirtualenvCommand(VirtualenvCommand):

    """Command for deleting virtualenv directories."""

    def run(self, **kwargs):
        """Display quick panel with found virtualenvs."""
        self.available_venvs = self.find_virtualenvs()
        self.window.show_quick_panel(self.available_venvs, self.remove_virtualenv)

    def remove_virtualenv(self, index):
        """Request confirmation and delete the directory tree.

        Also set current virtualenv to None.
        """
        if index == -1:
            return

        venv = self.available_venvs[index][1]
        confirmed = sublime.ok_cancel_dialog(
            "Please confirm deletion of virtualenv at:\n\"{}\".".format(venv))
        if confirmed:
            try:
                shutil.rmtree(venv)
                logger.info("\"{}\" deleted.".format(venv))
            except (IOError, OSError):
                logger.error("Could not delete \"{}\".".format(venv))
            else:
                if venv == self.get_virtualenv():
                    self.set_virtualenv(None)


class AddVirtualenvDirectoryCommand(VirtualenvCommand):

    """Shortcut command for adding paths to the 'virtualenv_directories' setting."""

    def run(self, **kwargs):
        """Shot input panel requesting path to user."""
        self.window.show_input_panel(
            "Directory path:", os.path.expanduser("~") + os.path.sep,
            self.add_directory, None, None)

    def add_directory(self, directory):
        """Add given directory to the list.

        If the path is not a directory show error dialog.
        """
        if not directory:
            return

        directory = os.path.expanduser(os.path.normpath(directory))
        if not os.path.isdir(directory):
            sublime.error_message("\"{}\" is not a directory.".format(directory))
            return

        directories = self.virtualenv_directories
        directories.append(directory)
        settings().set('virtualenv_directories', directories)
        settings.save()
