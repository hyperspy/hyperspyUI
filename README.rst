HyperSpyUI
==========

|pypi_version|_

.. |pypi_downloads| image:: http://img.shields.io/pypi/dm/hyperspyui.svg?style=flat
.. _pypi_downloads: https://pypi.python.org/pypi/hyperspyui

.. |pypi_version| image:: http://img.shields.io/pypi/v/hyperspyui.svg?style=flat
.. _pypi_version: https://pypi.python.org/pypi/hyperspyui

HyperSpyUI tries to bring a streamlined user interface to the powerful
multi-dimensional analysis capabilities of HyperSpy_. HyperSpy is an open
source Python library which provides tools to facilitate data analysis of
multidimensional datasets.

HyperSpy aims at making it easy and natural to apply analytical procedures
that operate on an individual signal to multidimensional arrays, as well as
providing easy access to analytical tools that exploit the multidimensionality
of the dataset.

While the UI tries to create a simple and intuitive interface to HyperSpy, it
still retains the raw power of HyperSpy via the UI’s built in IPython console,
which runs on the same Python kernel as the UI.


Installation
=============
There are several ways to install HyperSpyUI. The application itself is rather
simple to install, but its dependencies can be a bit more tricky.

Bundle Installer
----------------
If you're on Windows, the quickest way to get set up is to download and install
the HyperSpyUI bundle installer. The bundled WinPython_ distribution includes
all the dependencies of the program, and the installer also helps create
program shortucts and register common microscopy file formats with the
application.

The bundle installer can also be used if you already have installed a WinPython
distribution (e.g. via the `HyperSpy bundle`_), and just want to add HyperSpyUI
and its dependencies, although it might not support older versions.

.. _WinPython: http://winpython.github.io/
.. _HyperSpy bundle: http://hyperspy.org/download.html

Installation via pip and conda
------------------------------
Due to a dependency on pyqt version 4 (version 5 is not currently supported), to install in a fresh anaconda environment, please use the following commands. Run each line separately, waiting for the previous line to finish. The "activate UI" line must be used before starting hyperspyui in any new terminal or command window.

.. code-block:: bash

    conda create --name UI python=3.5 numpy hyperspy
    activate UI
  
    pip install hyperspyui

    conda install -c menpo pyqt=4

And run it with:

.. code-block:: bash

    python -m hyperspyui

For further information, see the full documentation_.

.. _HyperSpy: http://hyperspy.org
.. _documentation: http://hyperspy.org/hyperspyUI/
