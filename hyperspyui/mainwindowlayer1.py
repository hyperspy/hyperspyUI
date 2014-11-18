# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 21:17:42 2014

@author: vidarton
"""

# Set proper backend for matplotlib
import matplotlib
matplotlib.use('module://mdi_mpl_backend')
matplotlib.interactive(True)

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)

from consolewidget import ConsoleWidget

import mdi_mpl_backend


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
        self.toolbar_button_unit = 32   #TODO: Make a property
        self.default_fig_floating = False
        self.default_widget_floating = False
        
        # Collections
        self.widgets = []   # Widgets in widget bar
        self.figures = []   # Matplotlib figures
        self.actions = {}
        self.toolbars = {}
        self.menus = {}
        
        # MPL backend bindings
        mdi_mpl_backend.connect_on_new_figure(self.on_new_figure)
        mdi_mpl_backend.connect_on_destroy(self.on_destroy_figure)
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        self.main_frame = QMdiArea()

        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.create_default_actions()   # Goes before menu/toolbar/widgetbar
        
        self.create_console()   # Needs to go before menu, so console can be in menu
        self.create_menu()  # This needs to happen before the widgetbar and toolbar
        self.create_toolbars()
        self.create_widgetbar()
        
        self.setCentralWidget(self.main_frame)
        
    def create_default_actions(self):
        pass
    
    def create_menu(self):
        mb = self.menuBar()
        # Window menu is filled in add_widget and add_figure
        self.windowmenu = mb.addMenu(tr("&Windows"))
        self.windowmenu.addAction(self._console_dock.toggleViewAction())
        # Figure windows go below this separator. Other windows can be added
        # above it with insertAction(self.windowmenu_sep, QAction)
        self.windowmenu_sep = self.windowmenu.addSeparator()
    
    def create_toolbars(self):
        """
        Override to create toolbars and toolbar buttons on UI construction.
        It is called after create_default_action(), so add_toolbar_button()
        can be used to add previously defined acctions.
        """
        pass
    
    def set_status(self, msg):
        """
        Display 'msg' in window's statusbar.
        """
        # TODO: What info is needed? Add simple label first, create utility to add more?
        self.statusBar().showMessage(msg)
    
    def create_widgetbar(self):
        """
        The widget bar itself is created and managed implicitly by Qt. Override
        this function to add widgets on UI construction.
        """
        pass
    
    def load_preferences(self):
        # TODO: Figure out standard location for python apps to store prefs
        pass
    
    def save_preferences(self):
        pass
    
    # --------- MPL Events ---------
    
    def on_new_figure(self, figure, userdata=None):
        """
        Callback for MPL backend.
        """
        self.main_frame.addSubWindow(figure)
        self.figures.append(figure)
        self.windowmenu.addAction(figure.activateAction())
    
    def on_destroy_figure(self, figure, userdata=None):
        """
        Callback for MPL backend.
        """
        if figure in self.figures:
            self.figures.remove(figure)  
        self.windowmenu.removeAction(figure.activateAction()) 
            
    # --------- End MPL Events ---------
  
  
    # --------- UI utility finctions ---------
  
    def add_action(self, key, label, callback, tip=None, icon=None, shortcut=None, userdata=None):
        """
        Create and add a QAction to self.actions[key]. 'label' is used as the
        short description of the action, and 'tip' as the long description.
        The tip is typically shown in the statusbar. The callback is called 
        when the action is triggered(), and is called with the 'userdata' as
        a parameter if a non-None value was supplied. The optional 'icon' 
        should either be a QIcon, or a path to an icon file, and is used to
        depict the action on toolbar buttons and in menus.
        """
        #TODO: Add callbacks that are triggered on window activation / signal selection,
        # this can change the action (e.g. target), or enable/disable the action
        if icon is None:
            ac = QAction(tr(label), self)
        else:
            if not isinstance(icon, QIcon):
                icon = QIcon(icon)
            ac = QAction(icon, tr(label), self)
        if shortcut is not None:
            ac.setShortcuts(shortcut)
        if tip is not None:
            ac.setStatusTip(tr(tip))
        if userdata is None:
            self.connect(ac, SIGNAL('triggered()'), callback)
        else:
            def callback_udwrap():
                callback(userdata)
            self.connect(ac, SIGNAL('triggered()'), callback_udwrap)
        self.actions[key] = ac
    
    def add_toolbar_button(self, category, action):
        """
        Add the supplied 'action' as a toolbar button. If the toolbar defined
        by 'cateogry' does not exist, it will be created in 
        self.toolbars[category].
        """
        if self.toolbars.has_key(category):
            tb = self.toolbars[category]
        else:
            tb = QToolBar(tr(category), self)
            self.addToolBar(Qt.LeftToolBarArea, tb)
            self.toolbars[category] = tb
        
        if not isinstance(action, QAction):
            action = self.actions[action]
        tb.addAction(action)
        
    
    def add_menuitem(self):
        #TODO: Implement, and figure out parameters
        pass
    
    def add_widget(self, widget):
        """
        Add the passed 'widget' to the main window. If the widget is not a
        QDockWidget, it will be wrapped in one. The QDockWidget is returned.
        The widget is also added to the window menu self.windowmenu, so that
        it's visibility can be toggled.
        """
        if isinstance(widget, QDockWidget):
            d = widget
        else:
            d = QDockWidget(self)
            d.setWidget(widget)
            d.setWindowTitle(widget.windowTitle())
        d.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea) 
        self.addDockWidget(Qt.RightDockWidgetArea, d)
        d.setFloating(self.default_widget_floating)
        
        # Insert widgets in Windows menu before separator (figures are after)
        self.windowmenu.insertAction(self.windowmenu_sep, d.toggleViewAction())
        return d
        
    def show_okcancel_dialog(self, title, widget, modal=True):
        diag = QDialog(self)
        diag.setWindowTitle(title)
        diag.setWindowFlags(Qt.Tool)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                Qt.Horizontal, diag)                        
        btns.accepted.connect(diag.accept)
        btns.rejected.connect(diag.reject)
        
        box = QVBoxLayout(diag)
        box.addWidget(widget)
        box.addWidget(btns)
        diag.setLayout(box)
        
        if modal:
            diag.exec_()
        else:
            diag.show()
        # Return the dialog for result checking, and to keep widget in scope for caller
        return diag
  
  
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