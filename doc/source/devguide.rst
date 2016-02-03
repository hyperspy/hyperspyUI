
Developer guide
===============


This guide is intended for anyone that wants to write code that interacts
with the UI. This can be relevant for tasks from gaining access to the loaded
signals in the console, to writing plugins that extended the functionality of
the UI.

One of the main components of the API is the 
:py:class:`~hyperspyui.mainwindow.MainWindow` class. This is the class of
the main UI window, and can be considered the hub to reach all the loaded
content, including signals and models, or :ref:`actions`,
:ref:`widgets-section` and :ref:`tools-section`.


.. _console:

Internal Console
----------------

The internal console is a qtconsole_ console widget running IPython_, and can
run any code that IPython can. To facilitate the typical use of the console,
numpy_ is pre-loaded as ``np``, and :py:mod:`hyperspy.api` as ``hs``. The current
:py:class:`~hyperspyui.mainwindow.MainWindow` instance is also exported as
``ui``, and the list of currently loaded hyperspy 
:py:class:`~hyperspy.signals.Signal` instances is exported as ``siglist``.

.. _qtconsole: https://qtconsole.readthedocs.org/en/stable/
.. _IPython: http://ipython.org/
.. _numpy: http://www.numpy.org/

If we want to inspect the original metadata of the currently selected signal,
we can then run::
    
    In [1]: s = ui.get_selected_signal()

    In [2]: s.original_metadata
    Out[2]: 
    ├── DATATYPE = Y
    ├── FORMAT = EMSA/MAS Spectral Data File
    ├── NCOLUMNS = 1.0
    ├── NPOINTS = 2048.0
    ├── OFFSET = 360.0
    ├── OWNER = 
    ├── SIGNALTYPE = ELS
    ├── TITLE = 
    ├── VERSION = 1.0
    ├── XPERCHAN = 0.2
    ├── XUNITS = eV
    └── YUNITS = Counts



.. _code-editor:

Code editor widget
------------------

Code editor widgets allow you to edit Python code directly within the
application. This can be useful for :ref:`recording` code, or for creating
and modifying :ref:`plugins` on the fly. An editor widget is opened when
the :ref:`new-editor` action is triggered, when a python script is opened,
or when recording is started via the :ref:`recorder-widget`.



.. _plugin-manager-widget:

Plugin manager widget
---------------------

The plugin manager widget shows a list of all the discovered plugins 
(and any that have been added manually), their locations, and allows 
to set whether they should be loaded or not. There's also an 'Edit' button
which will open up the source code of the plugin in a new :ref:`code-editor`.

Unselecting a plugin will attempt to unload it, but the success of this
depends on the plugin correctly implementing its 
:py:meth:`~hyperspyui.plugins.plugin.unload` routine, which might not always
be the case.

.. note::
    The unloading will only be partial if references to its content
    remain elsewhere in the program, so for this reason many core plugins will 
    fail to unload fully.
