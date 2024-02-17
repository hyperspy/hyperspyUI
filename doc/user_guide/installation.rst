
Installation
=============

There are several ways to install HyperSpyUI. The application itself is rather
simple to install, but its dependencies can be a bit more tricky.

Bundle Installer
-----------------

If you're on Windows, the quickest way to get set up is to download and install
the `HyperSpy bundle`_ installer.

.. _HyperSpy bundle: https://github.com/hyperspy/hyperspy-bundle


Install via `conda`
-------------------

HyperSpyUI can also be installed in an Anaconda_ or Miniconda_ distribution
using ``conda``:

.. code-block:: bash

   conda install -c conda-forge hyperspyui


.. _Anaconda: https://www.anaconda.com/distribution/
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html


Install via `pip`
-----------------

HyperSpyUI is on PyPI_, so simply run the command

.. code-block:: bash

   pip install hyperspyui[all]


which will download and install HyperSpyUI and its dependencies (including optional dependencies
and ``pyqt``). The package defines a GUI script ``hyperspyui``, which can be called to start the
application, or alternatively it can be started by running ``python -m hyperspyui``.

HyperSpyUI requires ``pyqt`` or ``pyside`` to be installed. If you want to use ``pyside``, you can
install HyperSpyUI without the ``all`` extra. Similarly, to install HyperSpyUI without its optional
dependencies, use:

.. code-block:: bash

   pip install hyperspyui


To get HyperSpyUI to integrate with your operating system after installation,
run:

.. code-block:: bash

   python -m hyperspyui.desktop_integration


Append the ``--help`` flag for other options.

Currently, this only integrates with Windows and Linux, but this is intended to 
be extend to MacOS systems in the future (please consider contributing).

.. _PyPI: https://pypi.python.org/pypi/hyperspyUI


Getting Qt
""""""""""
Getting and installing Qt_ might or might not be easy, depending on which
operating system you are on. For this reason, it is recommended to run
HyperSpyUI on a distribution which offers ready-made Qt packages. Examples
include WinPython_, Anaconda_ and Miniconda_.

.. _WinPython: https://winpython.github.io/
.. _Qt: https://www.qt.io/


