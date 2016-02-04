
Quickstart Guide
================

This guide is designed to help you get up and running quickly with HyperSpyUI.

.. .. contents::
..    :local:
..    :depth: 2


Launch
--------------

Sarting the HyperSpyUI application can be dependent on how it was installed.
If it was installed into the OS, a shortcut might have been created on your
desktop, and running the shortcut should then be enough to start the program.

If you do not have a shortcut, the app can typically be started by running
the command ``python -m hyperspyui.launch``. This assumes that the python
command is available from wherever you are running it. If that is not the case,
figure out the full path to the python executable, and run it as above 
``<full path>/python -m hyperspyui.launch``.

The final option is to fully explicit::
    
    <full path to python>/python "<full path to hyperspyui>/launch.py"


Overview
--------------

The user interface is based on top of Qt_, and have four main components:

.. image:: ui_overview.png

.. _Qt: http://www.qt.io/

    #)  Menus: Most of the actions you can do have a menu entry.
    #)  Toolbars: Several actions have their own button on a toolbar, and all
        interactive :ref:`tools-section` are here as well.
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
one of the `file types`_ that HyperSpy can read. This can either be achived
by dragging and dropping the file in question onto the application window,
or by the open file dialog accessible in the toolbar (|open button|), or
from the File menu.

.. |open button| image:: ../../hyperspyui/images/open.svg
    :width: 18 px
.. _file types: http://hyperspy.org/hyperspy-doc/current/user_guide/io.html#supported-formats

If you have registered the application with the operating system to handle the
file types, files can also be opened in HyperSpyUI simply by opening them in
a normal file browser.

Once the file is loaded, the resulting HyperSpy signal should automatically
be plotted. If not, an error might have occured, in which case you should
check your :ref:`error-output`.

Once the signal is loaded, you are ready to start inspecing and manipulating
your data. See the following sections for a more detailed explanation of
what can be done, or simply start playing around! It normally takes quite
a conscious effort to overwrite existing data ("save" action, pick existing
file name, confirm "yes I want to overwrite" dialog), so you should be
safe in playing around.
