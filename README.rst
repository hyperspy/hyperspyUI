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

Bundle Installer on Windows
---------------------------
If you're on Windows, the quickest way to get set up is to download and install
the `HyperSpy bundle`_ installer, which includes HyperSpyUI.

.. _HyperSpy bundle: https://github.com/hyperspy/hyperspy-bundle

Anaconda/Miniconda on Mac or Linux
----------------------------------

Download and install the `Miniconda`_ distribution and run the following command 
in the anaconda prompt: 

.. code-block:: bash

    conda install -c conda-forge hyperspy
    pip install hyperspyui

.. _Miniconda: https://conda.io/miniconda.html

Installation via pip
--------------------

HyperSpyUI can be intall from pip. Depending on your python distribution you may 
need to have C compiler on your system to install some of the dependencies.

.. code-block:: bash

    pip install hyperspyui
   

After installation, you can run HyperSpyUI from the command prompt with:

.. code-block:: bash

    python -m hyperspyui

For further information, see the full documentation_.

.. _HyperSpy: http://hyperspy.org
.. _documentation: http://hyperspy.org/hyperspyUI/
