# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 21:17:42 2014

@author: Vidar Tonaas Fauske
"""

# Set proper backend for matplotlib
import matplotlib
matplotlib.use('module://hyperspyui.mdi_mpl_backend')
matplotlib.interactive(True)

import os

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *


def tr(text):
    return QCoreApplication.translate("MainWindow", text)

from widgets.consolewidget import ConsoleWidget
import hyperspyui.mdi_mpl_backend
from pluginmanager import PluginManager


class MainWindowLayer1(QMainWindow):

    """
    Base layer in application stack. Should handle the connection to our custom
    matplotlib backend, and manage the Figures. As such, it does not know
    anything about hyperspy, and can readily be reused for other projects.
    Should also set up basic UI with utilities, and relevant functions for
    inhereting classes to override.
    """

    def __init__(self, parent=None):
        super(MainWindowLayer1, self).__init__(parent)

        # Properties
        self.toolbar_button_unit = 32  # TODO: Make a property
        self.default_widget_floating = False
        self.cur_dir = ""

        # Read settings
        self.read_settings()

        # State varaibles
        self.should_capture_traits = None
        self.active_tool = None

        # Collections
        self.widgets = []   # Widgets in widget bar
        self.figures = []   # Matplotlib figures
        self.editors = []   # EditorWidgets
        self.traits_dialogs = []
        self.actions = {}
        self._action_selection_cbs = {}
        self.toolbars = {}
        self.menus = {}
        self.tools = []
        self.plugin_manager = None

        # MPL backend bindings
        hyperspyui.mdi_mpl_backend.connect_on_new_figure(self.on_new_figure)
        hyperspyui.mdi_mpl_backend.connect_on_destroy(self.on_destroy_figure)

        # Create UI
        self.windowmenu = None
        self.create_ui()

        # Connect figure management functions
        self.main_frame.subWindowActivated.connect(self.on_subwin_activated)

    @property
    def plugins(self):
        return self.plugin_manager.plugins

    def handleSecondInstance(self, argv):
        # overload if needed
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized |
                            QtCore.Qt.WindowActive)
        self.activateWindow()

    def create_ui(self):
        self.setIconSize(
            QSize(self.toolbar_button_unit, self.toolbar_button_unit))
        self.main_frame = QMdiArea()

        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.init_plugins()

        self.create_default_actions()   # Goes before menu/toolbar/widgetbar

        # Needs to go before menu, so console can be in menu
        self.create_console()
        # This needs to happen before the widgetbar and toolbar
        self.create_menu()
        self.create_toolbars()
        self.create_widgetbar()

        self.setCentralWidget(self.main_frame)

    def init_plugins(self):
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.init_plugins()

    def create_default_actions(self):
        """
        Create default actions that can be used for e.g. toolbars and menus,
        or triggered manually.
        """
        self.plugin_manager.create_actions()

        self.selectable_tools = QActionGroup(self)
        self.selectable_tools.setExclusive(True)

    def create_menu(self):
        mb = self.menuBar()
        # Window menu is filled in add_widget and add_figure
        self.windowmenu = mb.addMenu(tr("&Windows"))
        self.windowmenu.addAction(self._console_dock.toggleViewAction())
        # Figure windows go below this separator. Other windows can be added
        # above it with insertAction(self.windowmenu_sep, QAction)
        self.windowmenu_sep = self.windowmenu.addSeparator()

        self.plugin_manager.create_menu()

    def create_tools(self):
        """Override to create tools on UI construction.
        """
        self.plugin_manager.create_tools()

    def create_toolbars(self):
        """
        Override to create toolbars and toolbar buttons on UI construction.
        It is called after create_default_action(), so add_toolbar_button()
        can be used to add previously defined acctions.
        """
        self.create_tools()
        self.plugin_manager.create_toolbars()

    def create_widgetbar(self):
        """
        The widget bar itself is created and managed implicitly by Qt. Override
        this function to add widgets on UI construction.
        """

        self.plugin_manager.create_widgets()

    def select_tool(self, tool):
        if self.active_tool is not None:
            self.active_tool.disconnect(self.figures)
        self.active_tool = tool
        tool.connect(self.figures)

    def closeEvent(self, event):
        self.write_settings()

    # --------- Figure management ---------

    # --------- MPL Events ---------

    def on_new_figure(self, figure, userdata=None):
        """
        Callback for MPL backend.
        """
        self.main_frame.addSubWindow(figure)
        self.figures.append(figure)
        self.windowmenu.addAction(figure.activateAction())
        for tool in self.tools:
            if tool.single_action() is not None:
                tool.connect(figure)
        if self.active_tool is not None:
            self.active_tool.connect(figure)

    def on_destroy_figure(self, figure, userdata=None):
        """
        Callback for MPL backend.
        """
        if figure in self.figures:
            self.figures.remove(figure)
        self.windowmenu.removeAction(figure.activateAction())
        for tool in self.tools:
            if tool.single_action() is not None:
                tool.disconnect(figure)
        if self.active_tool is not None:
            self.active_tool.disconnect(figure)
        self.main_frame.removeSubWindow(figure)

    # --------- End MPL Events ---------

    def on_subwin_activated(self, mdi_figure):
        if mdi_figure and os.environ['QT_API'] == 'pyside':
            mdi_figure.activateAction().setChecked(True)
        self.check_action_selections(mdi_figure)

    def check_action_selections(self, mdi_figure=None):
        if mdi_figure is None:
            mdi_figure = self.main_frame.activeSubWindow()
        for key, cb in self._action_selection_cbs.iteritems():
            cb(mdi_figure, self.actions[key])

    # --------- End figure management ---------

    # --------- UI utility finctions ---------

    def get_figure_filepath_suggestion(self, figure, deault_ext=None):
        canvas = figure.widget()
        if deault_ext is None:
            deault_ext = canvas.get_default_filetype()

        f = canvas.get_default_filename()
        if not f:
            f = self.cur_dir

        # Analyze suggested filename
        base, tail = os.path.split(f)
        fn, ext = os.path.splitext(tail)

        # If no directory in filename, use self.cur_dir's dirname
        if base is None or base == "":
            base = os.path.dirname(self.cur_dir)
        # If extension is not valid, use the defualt
        if ext not in canvas.get_supported_filetypes():
            ext = deault_ext

        # Build suggestion and return
        path_suggestion = os.path.sep.join((base, fn))
        path_suggestion = os.path.extsep.join((path_suggestion, ext))
        return path_suggestion

    def save_figure(self, figure=None):
        if figure is None:
            figure = self.main_frame.activeSubWindow()
            if figure is None:
                return
        path_suggestion = self.get_figure_filepath_suggestion(figure)
        canvas = figure.widget()

        # Build type selection string
        def_type = os.path.extsep + canvas.get_default_filetype()
        extensions = canvas.get_supported_filetypes_grouped()
        type_choices = u"All types (*.*)"
        for group, exts in extensions.iteritems():
            fmt = group + \
                ' (' + \
                '; '.join([os.path.extsep + sube for sube in exts]) + ')'
            type_choices = ';;'.join((type_choices, fmt))
            if def_type[1:] in exts:
                def_type = fmt

        # Present filename prompt
        filename = QFileDialog.getSaveFileName(self, tr("Save file"),
                                               path_suggestion, type_choices,
                                               def_type)[0]
        if filename:
            canvas.figure.savefig(filename)

    # --------- Settings ---------

    def write_settings(self):
        s = QSettings(self)
        s.beginGroup("mainwindow")
        s.setValue('toolbar_button_unit', self.toolbar_button_unit)
        s.setValue('default_widget_floating', self.default_widget_floating)
        s.endGroup()
        s.setValue('cd', self.cur_dir)

    def read_settings(self):
        s = QSettings(self)
        s.beginGroup("mainwindow")
        self.toolbar_button_unit = s.value("toolbar_button_unit",
                                           self.toolbar_button_unit, int)
        self.default_widget_floating = s.value("default_widget_floating",
                                               self.default_widget_floating, bool)
        s.endGroup()
        cd = s.value('cd', None)
        if cd is not None and len(str(cd)) > 0:
            if self.cur_dir == "":
                self.cur_dir = str(cd)

    # --------- Console functions ---------

    def _get_console_exec(self):
        return ""

    def _get_console_exports(self):
        return {'ui': self}

    def _get_console_config(self):
        return None

    def on_console_executing(self, source):
        """
        Override when inherited to perform actions before exectuing 'source'.
        """
        pass

    def on_console_executed(self, response):
        """
        Override when inherited to perform actions after executing, given the
        'response' returned.
        """
        pass

    def create_console(self):
        # TODO: Reroute STDOUT/STDERR to console. Maybe only for actions?
        # We could inherit QAction, and have it reroute when it triggers,
        # and then drop route when it finishes, however this will not catch
        # interactive dialogs and such.
        c = self._get_console_config()
        control = ConsoleWidget(config=c)
        control.executing.connect(self.on_console_executing)
        control.executed.connect(self.on_console_executed)

        # This is where we push variables to the console
        ex = self._get_console_exec()
        push = self._get_console_exports()
        control.ex(ex)
        control.push(push)

        self.console = control

        self._console_dock = QDockWidget()
        self._console_dock.setWidget(control)
        self._console_dock.setWindowTitle("Console")
        self.addDockWidget(Qt.BottomDockWidgetArea, self._console_dock)
