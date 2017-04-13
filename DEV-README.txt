
A guide for adding functionality for HyperSpyUI
===================================================


To add simple functionality to the UI, a full understanding of the UI framework
should not be necessary. However, it it useful to understand how HyperSpy 
signals are wrapped by the SignalWrapper class, as this is responsible for
tracking a signal's figures, and persisting certain properties across replots.
That being said, otherwise it should be pretty straightforward to add 
functionality to the UI. Other than that, see the API docs further down.

Features can currently be implemented three ways:
 1) Actions:
    Actions are a common name for something that is triggered as a response to
    user input, e.g. clicking an entry in the menu, or clicking a button in 
    the toolbar. It is associated with a callback, and several attributes
    which can represent the action to the user. Once an action has been 
    created, it can easily be added to the menu or toolbar. It is recommended 
    to create actions through MainWindow's method add_action, but it is also 
    possible to create them independently (see QT's docs for QAction). Once an
    action has been created, it can be added to the toolbar and menu by using 
    MainWindow's add_toolbar_button() and add_menuitem(), which also takes a 
    'category' argument, which defines which toolbar or menu to put the action
    in.

 2) Tools:
    Tools are a little more complex than actions, but mainly consists of 
    FigureTools, which are tools that interact with a figure. FigureTools can
    again be divided into two subtypes: Single action tools, and selectable 
    tools. Single action tools are very similar to normal actions, in that they
    perform an action when the tool is clicked, but they also listen to MPL 
    events on all figures. Selectable tools are mutually exclusive, so that 
    only one selectable tools can be active at the same time, and are connected
    and disconnected from MPL events as the tool changes its selected state.

    An example of a selectable tool is the crop tool, which allows the user to
    select an ROI on a figure with a widget, and then crop the signal to the 
    ROI.

    To create a tool, subclass either Tool or FigureTool.

 3) Permanent widgets:
    Widgets are small windows that can either be docked in the sidebar, or 
    floating. Widgets added this way can be hidden, but can always be displayed
    via the Windows menu. If considering to add a widget this way, always think
    through whether it should be a permanent widget, or a dialog that pops up
    when an action is triggered. The distinction isn't always easy to make, but
    dialogs are better for single instance input events, or when it would be 
    too resource heavy to have it permanently active.

Widgets, whether for dialogs or permanent widgets can be any QWidget (although
it needs to resize correctly to fit in the permanent widget sidebar). This 
means they can easily be created using e.g. Qt Designer


Once you have decided how to implement your features, you need to decide how to
add them to the UI: Directly in the codebase, or as a plugin. Normally, all 
features should be added as a plugin, as these can then simply be dropped into
the plugin folder to add behavior, and no special loading code is need in the
main codebase. However, if you feel that the features should be a part of the
program core, please add its load code to the MainWindow class, normally in the
create_*() methods.


-------------------------------
Plugins
-------------------------------

To create a plugin, subclass hyperspyui.plugins.plugin.Plugin, and overload
the create_*() methods as appropriate to load and register your features.
The different create functions should be pretty self explanatory, but please use
the core plugins as examples if in doubt. As long as it works, and does not 
interfere with other pluigns/features, it should be OK.

To specify the name of the plugin, set the static 'name' attribute on your
class. If not set, the class name will be used to represent the plugin.

Each plugin has its own settings, which can be accessed through the 'settings'
attribute. Get or set the settings by indexing with a key (will be converted 
to string), as you would for a dict. When reading a settings, it will be 
returned as a string, unless a type is specified as the second index:

my_float_as_string = my_plugin.settings['my_float']
my_float_value = my_plugin.settings['my_float', float]

Note, the type conversion is handled by QSettings, so consult its docs for
expected behavior and supported types.

The Settings class also has the utility function get_or_prompt, which either
fetches a previously specified setting, or prompts the user for it. The prompt
will then have a "Remember this choice" checkbox, which if checked will store
the users selection in the specified setting key.

When the plugin is loaded, its create functions are called in the following 
order:
    create_actions()
    create_menu()
    create_toolbars()
    create_widgets()


-------------------------------
API
-------------------------------

Depending on what you want to do, you're likely to need to get certain 
information from the UI, e.g. which signal is the currently active one. As 
such, these are the currently implemented API functions and properties:

MainWindow.set_status():
    display a message in the status bar (displayed for a certain time). 
    Currently only a wrapper for MainWindow.statusBar().showMessage().

MainWindow.signals:
    This is a BindingsList (custom type), that mirrors its additions/removals 
    to connected lists or listwidgets. It also supports custom addition/removal
    callbacks, which can be repurposed as event notifications.

MainWindow.cur_dir:
    Current directory for input/output. Used by e.g. open and close methods.

MainWindow.widgets:
    List of permanent widgets

MainWindow.figures:
    List of all Matplotlib figures

MainWindow.actions:
    Dict acting as a central repository of actions. If adding an action, make
    sure that the action key is unique, preferably by prefixing all keys with
    e.g. your plugin name.

MainWindow.toolbars:
    Dict of toolbars, indexed by category name.

MainWindow.menus:
    Dict of menus, indexed by category name.

MainWindow.tools:
    List of all loaded tool instances.

MainWindow.plugin_manager
    Plugin manager. Currently there is no API functions on this, but in the 
    future this should allow plugins to load other plugins on the fly.

MainWindow.add_signal_figure():
    Wraps a hyperspy.Signal in a SignalWrapper, and adds the wrapper to 
    MainWindow.signals. Also plots the signal unless specified not to.

MainWindow.add_action():
    Creates an action that can be added to e.g. a toolbar or menu.

MainWindow.add_toolbar_button():
    Adds an action as a toolbar button.

MainWindow.add_menuitem():
    Adds an action to the application menu.

MainWindow.add_widget():
    Adds a permanent widget to either the widget sidebar, or floating, 
    depending on the MainWindow.default_widget_floating value. If not already
    a QDockWidget, the widget will be wrapped in one! If wrapped, the passed
    widget will still be the one that is added to MainWindow.widgets.

MainWindow.show_okcancel_dialog():
    Shows a passed widget as a dialog, but adds OK and Cancel buttons below it.

MainWindow.get_selected_signal():
    Gets the currently active SignalWrapper.

MainWindow.get_selected_signals():
    Gets a list of currently selected SignalWrappers (multi-selection through 
    the DataViewWidget on the side).

MainWindow.get_selected_model():
    Gets the currently active ModelWrapper. Tries to infer it if no obvious
    choice.

MainWindow.get_selected_component():
    Gets the currently active component. Tries to infer it if no obvious
    choice.

MainWindow.get_selected_plot():
    Gets the currently active plot. This is different from gcf/gca, in that it
    finds the selected signal, the active window, and tries to determine
    whether the window is either the navigation plot, signal plot, or some 
    other window. 

MainWindow.add_model():
    Creates a model for the passed/active signal. Uses SignalWrapper.make_model
    to create the ModelWrapper and add the linkage. Returns the created 
    ModelWrapper.

Mainwindow.make_component():
    Create a component, and add it to the selected model.

MainWindow.console:
    Instance of ConsoleWidget. See its docstrings for how to interact.

MainWindow.capture_traits_dialog():
    Setup a trap for a traits dialog, so that the dialog can be treated as an
    internal widget.

MainWindow.load():
    Load a signal, and add it via add_signal_figure().

MainWindow.save():
    Save a signal.

MainWindow.get_signal_filepath_suggestion():
    Suggest a file path for saving a signal.

MainWindow.save_figure():
    Save an MPL figure. If no figure specified, save the currently active one.

MainWindow.get_figure_filepath_suggestion():
    Suggest a filepath for saving an MPL figure.

MainWindow.close_signal():
    Close the specified signal.

MainWindow.close_all_signals():
    Close all signals.
