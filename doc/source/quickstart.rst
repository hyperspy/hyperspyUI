
Quickstart Guide
================

This guide is designed to help you get up and running quickly with HyperSpyUI.

.. .. contents::
..    :local:
..    :depth: 2



Overview
--------------

The user interface is based on top of Qt_, and have four main components:

.. image:: ui_overview.png

.. _Qt: http://www.qt.io/

    #)  Menu: Most of the actions you can do has a menu entry.
    #)  Toolbar: Several actions have their own button on a toolbar, and all
        interactive `tools`_ are here as well.
    #)  Widgets: These are small panels or windows that can be moved, and
        are always open unless explicitly closed. Their content and behavior
        can vary widely, and includes the `data tree` and the `console` widgets.
    #)  Figures: The final component are the figures and plots that are
        generated. These include all `matplotlib`_ figures, but the ones created
        by HyperSpy are the most interesting ones.

.. _matplotlib: http://matplotlib.org/


Loading data
--------------

The standard way of getting data into the application is to open a file of
one of the `files types`_ that HyperSpy can read. This can either be achived
by dragging and dropping the file in question onto the application window,
or by the open file dialog accessible in the toolbar (|open button|), or
from the File menu.

.. |open button| image:: open.svg
    :width: 18 px
.. _file types: http://hyperspy.org/hyperspy-doc/current/user_guide/io.html#supported-formats

If you have registered the application with the operating system to handle the
file types, files can also be opened in HyperSpyUI simply by opening them in
a normal file browser.

Once the file is loaded, the resulting HyperSpy signal should automatically
be plotted. If not, an error might have occured, in which case you should
check your `error output`_.
