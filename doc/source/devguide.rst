
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
