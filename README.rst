HyperSpyUI
==========

|pypi_version|_ |anaconda_cloud|_ |tests|_ |python_version|_

.. |pypi_version| image:: https://img.shields.io/pypi/v/hyperspyui.svg
.. _pypi_version: https://pypi.python.org/pypi/hyperspyui

.. |anaconda_cloud| image:: https://anaconda.org/conda-forge/hyperspyui/badges/version.svg
.. _anaconda_cloud: https://anaconda.org/conda-forge/hyperspyui

.. |tests| image:: https://github.com/hyperspy/hyperspyUI/workflows/Tests/badge.svg
.. _tests: https://github.com/hyperspy/hyperspyUI/actions

.. |python_version| image:: https://img.shields.io/pypi/pyversions/hyperspyui.svg?style=flat
.. _python_version: https://pypi.python.org/pypi/hyperspyui

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

Documentation
=============

For an introduction to HyperSpyUI, see the documentation_.


Installation
============
There are several ways to install HyperSpyUI. The application itself is rather
simple to install, but its dependencies can be a bit more tricky. From version
1.1, HyperSpyUI supports both PyQt4 and PyQt5.

HyperSpy Bundle Installer
-------------------------
The quickest way to get set up is to download and install
the `HyperSpy bundle`_ installer, which includes HyperSpyUI.

.. _HyperSpy bundle: https://github.com/hyperspy/hyperspy-bundle

Anaconda/Miniconda/Miniforge
----------------------------

Download and install the `Miniforge`_ (`Miniconda`_ or `Anaconda`_) distribution
and run the following command in the anaconda prompt:

.. code-block:: bash

    conda install -c conda-forge hyperspyui

.. _Miniforge: https://github.com/conda-forge/miniforge#download
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Anaconda: https://www.anaconda.com/products/individual

Installation via pip
--------------------

HyperSpyUI can be intall from pip. Depending on your python distribution you may
need to have C compiler on your system to install some of the dependencies.

.. code-block:: bash

    pip install hyperspyui

If pyqt is not installed, run:

.. code-block:: bash

    pip install PyQt5 PyQtWebEngine


Run HyperSpyUI
==============

After installation, you can run HyperSpyUI from the command prompt with:

.. code-block:: bash

    hyperspyui

or

.. code-block:: bash

    python -m hyperspyui


For further information, see the full documentation_.

.. _HyperSpy: https://hyperspy.org
.. _documentation: https://hyperspy.org/hyperspyUI/
