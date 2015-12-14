HyperSpyUI
==========
A graphical interface for HyperSpy.

To install the current version as a user, run the following command (assuming
you have the package manager 'pip')::

    pip install hyperspyui

To install a development version, clone the git repository and run::

    pip install -e ./

from the hyperspyui root directory.

For both cases, to create desktop and start menu icons on windows, run the
installed script "hyperspyui_install.py". This will also associate .msa and
.hdf5 files with the UI. Similar behavior for linux is under development.

A GUI entry point is also defined, named "HyperSpyUI".