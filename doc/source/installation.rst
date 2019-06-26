
Installation
=============

There are several ways to install HyperSpyUI. The application itself is rather
simple to install, but its dependencies can be a bit more tricky.

Bundle Installer
-----------------

If you're on Windows, the quickest way to get set up is to download and install
the `HyperSpy Bundle installer <https://github.com/hyperspy/hyperspy-bundle>`_ that includes HyperSpyUI.

Install via `pip`
-----------------

HyperSpyUI is on PyPI_, so simply running the command ``pip install hyperspyui``
should download and install HyperSpyUI and its dependencies. The package defines
a GUI script ``hyperspyui``, which can be called to start the application, or
alternatively it can be started by running ``python -m hyperspyui``.

To get HyperSpyUI to integrate with your operating system after installation,
run:

.. code-block:: bash

   python -m hyperspyui.desktop_integration

Append the ``--help`` flag for other options.

Currently, this only
integrates with Windows and Linux, but this is intended to be extend to MacOS systems
in the future (please consider contributing).

.. _PyPI: https://pypi.python.org/pypi/hyperspyUI


Getting Qt
""""""""""
Getting and installing Qt_ might or might not be easy, depending on which
operating system you are on. For this reason, it is recommended to run
HyperSpyUI on a distribution which offers ready-made Qt packages. Examples
include WinPython_, Conda_ and Canopy_.

.. _Conda: https://github.com/conda/conda
.. _Canopy:

.. _Qt: https://www.qt.io/
