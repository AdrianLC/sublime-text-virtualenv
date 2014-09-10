Sublime Text - Virtualenv
=========================

Manage your virtualenvs directly from Sublime Text __3__.

## Features

- __Reusable build system__. Execute code with a virtualenv without
editing your paths manually.
- __Virtualenv search__. Finds virtualenvs in the open folders or _anywhere_ in your system.
- __Activation/Deactivation__. Select or disable the current virtualenv easily.
- __Create and delete virtualenvs__. With target python selection. Supports both the standard
[virtualenv][] package and the built-in [venv][pyvenv] module from Python 3.3.
- __Integration with other packages__. SublimeREPL.


## Support

Only Sublime Text 3. Tested in Linux and Windows but it should work in OS X as well.


## Installation

Install through Package Control as usual:

1. Open command palette through the menu or with `Ctrl+Shift+P`.
2. Select `Package Control: Install Package`.
3. Search _Virtualenv_ and press enter.

Detailed instructions [here][packageControl].


## Usage

#### Code Execution

Enable the `Python + Virtualenv` build system through the `Tools -> Build System` menu and execute with `Ctrl+B`. If you do not have any other custom Python builds defined, `Automatic` should work too.

The build system works with or without an activated virtualenv, so it can be used as default build for Python.

#### Activate

Search `Virtualenv: Activate` in the command palette and select the desired virtualenv.

#### Deactivate

The command `Virtualenv: Deactivate` is available when a virtualenv is activated.

#### Creating a virtualenv

Choose `Virtualenv: New` (or `Virtualenv: New (venv)` for built-in virtualenv), type a destination
path and select a python binary. The new virtualenv will be activated automatically.

#### Deleting a virtualenv

Use the command `Virtualenv: Remove`, choose a virtualenv and confirm.

#### Integrations

Launch a Python REPL using the current virtualenv with the command `Virtualenv: SublimeREPL - Python`.


## Settings

The list of default settings is available through `Preferences -> Package Settings -> Virtualenv -> Default`. Do not modify the default settings as you will lose all the changes if the package is updated. You should override the necessary settings in `Package Settings -> Virtualenv -> User` instead.

#### executable

The executable used for virtualenv creation. Defaults to `python -m virtualenv`, assuming that virtualenv is installed on the default python prefix.
Depending on your setup you might want to change this to something like: `virtualenv`, `virtualenv-3.3`, `python3 -m virtualenv`, etc.

#### virtualenv_directories

A list of directory paths searched for virtualenvs. By default, includes [virtualenvwrapper][]'s `WORKON_HOME`. `~/.virtualenvs` in Linux and OS X, and `~\Envs` in Windows ([virtualenvwrapper-win][]).

There is a shortcut command for quickly adding a virtualenv directory to your settings: `Virtualenv: Add directory`.

#### extra_paths

Additional paths searched for python binaries. It might be useful in case of portable python installations. Defaults to none.


## Advanced

The current virtualenv path is stored in the project settings and can be edited manually if the project has been saved to a `*.sublime-project` file.

Extending or customizing the build system should be possible. Just set `"target": "virtualenv_exec"` in your build system definition, or import and inherit from `Virtualenv.commands.VirtualenvExecCommand`. More information on Sublime Text's build systems [here][buildSystems].


## Future plans

Just some ideas for possible improvements.

- Integration with more packages. Paths for [SublimeCodeIntel][]?
- _Brother_ package for `pip` commands.




[packageControl]: https://sublime.wbond.net/docs/usage "Package Control"
[buildSystems]: http://sublime-text-unofficial-documentation.readthedocs.org/en/latest/reference/build_systems.html "Sublime Text build systems"
[virtualenv]: https://virtualenv.pypa.io/en/latest/ "virtualenv"
[virtualenvwrapper]: http://virtualenvwrapper.readthedocs.org/en/latest/ "virtualenvwrapper"
[virtualenvwrapper-win]: https://github.com/davidmarble/virtualenvwrapper-win/ "virtualenvwrapper-win"
[pyvenv]: https://docs.python.org/3.3/library/venv.html "pyvenv"
[SublimeREPL]: https://github.com/wuub/SublimeREPL "SublimeREPL"
[SublimeCodeIntel]: http://sublimecodeintel.github.io/SublimeCodeIntel/ "SublimeCodeIntel"
