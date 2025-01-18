
.. _settings-section:
    
Settings
===================

This section documents all the settings of the application and the core plugins.
To edit the settings use the the :ref:`edit-settings` action from the 'Settings'
menu. This will show a
:py:class:`hyperspyui.widgets.settingsdialog.SettingsDialog`, which lists all
the settings that have been stored or registered. It also has a 'Reset' button
to reset all the settings to their default values.

The settiings are grouped by category and/or plugin name, as reflected in the
listing below.

General
------------------

General application settings that are not specific to a certain task.

Allow multiple instances
""""""""""""""""""""""""""
If false (the default), only a single instance of the application can run at the
time. Any other instances that try to open will simply fail to materialize. If
true, many concurrent instances of the application can run, but with this setting
any attempts to open a file directly from the operating system will spawn a new
instance of the application in which that file is opened.

.. note::
    Concurrent applications instances will share their settings, as they are
    written and read on demand.

.. _output-to-console:


Console completion type
""""""""""""""""""""""""""
Set which completer to use for the qtconsole. See 
:py:attr:`qtconsole.console_widget.ConsoleWidget.gui_completion` for 
details on this setting.


Default widget floating
""""""""""""""""""""""""""
This settings determines how a widget is created when opened for the first 
time: Floating, or docked. After the first time, the layout and floating
state of the widgets will be stored, unless reset by the 
:ref:`reset-layout` action.


Low process priority
""""""""""""""""""""""""""
Set this to give the application a lower process priority, which will give
it a lower share of the processing power of the computer in order not to
affect other applications.


Output to console
""""""""""""""""""""""""""
When set, the :ref:`error-output` of the application will be redirected
to the :ref:`console-widget` after the application has successfully loaded.
This might make it easier to keep track of warnings and non-critical errors
while running, but will prevent the output from reacing the standard error
ouputs. This setting should therefore be disabled when debugging, or when 
creating a log for sharing in `e.g.` a bug report.


Toolbar button size
""""""""""""""""""""""""""
Specify the size of the toolbar buttons in units of pixels. Depending on your 
display resolution the default size might be too big or too small.

.. note::
    If you're running out of space for the toolbars, it is possible (and
    recommended) to rearrange them into several columns. Simply drag and
    drop the toolbars using the small handles on the top/left. It is also
    possible to arrange the toolbars along the top row of the application
    if that suits you better.

Working directory
""""""""""""""""""""""""""
This stores the last directory/file that was opened/saved to. Used for
having the dialogs open where they were last used.



.. _alignment-settings:

Align
----------------------

Settings of the alignment plugin.

1D smooth amount
""""""""""""""""""""""""""
Used by :ref:`alignment-horz` and :ref:`alignment-vert` to specify how
much to smooth the data in the direction of alignment. The smmothing is
done by a box-car convolution, and the setting specifies the size of the
box-car.

2D smooth amount
""""""""""""""""""""""""""
Used by :ref:`alignment-tool`. Specifies an optional amount of gaussian blur
filter to apply before alignment to reduce the effect of noise.


Parameters to hyperspy
""""""""""""""""""""""""""
The other settings are direct options for the parameters to pass to 
:py:meth:`hyperspy.signal.Signal2DTools.estimate_shift2D`. 



Basic signal tools
----------------------

Histogram bins method
""""""""""""""""""""""""""
What to pass for the ``bins`` parameter to
:py:meth:hyperspy.signal.get_histogram`.


Gaussian filter / Image rotation
----------------------------------

These plugins only store the values of their respective dialog boxes, so
changing these only affects the settings for the next time the dialog
launches. Can be useful in order to turn of the 'preview' feature in the
rotation dialog before attempting to rotate a very large signal.


MVA
----------------------

The settings of the multivariate analysis plugin, that supply the decomposition
actions.

Convert or copy
""""""""""""""""""""""""""
If set, this stores wheter a signals data type should be converted to float
before decomposition, or whether the decompoistion should be performed on a 
copy of the signal. If unset, a dialog box will pop up if a signal with the
wrong data type is selected for decomposition.



Version selector
----------------------

Stores settings for the cersion selector plugin, which affects the 
:ref:`version-selector` and :ref:`check-for-updates` action. The
settings of this plugin is only relevant if you have a source installation
of a git repository (developer mode).

Check for git updates
""""""""""""""""""""""""""
Currently unused.

Git executable
""""""""""""""""""""""""""
The path to the git executable, if it is not available on PATH. If not
supplied, and not on path, a file browser will pop up asking to locate the
executable when needed. If an executable is found, it will be stored in 
this setting.

