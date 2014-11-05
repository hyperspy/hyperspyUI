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

from ConsoleWidget import ConsoleWidget

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
        pass
    
    def set_status(self, msg):
        # TODO: What info is needed? Add simple label first, create utility to add more?
        self.statusBar().showMessage(msg)
    
    def create_widgetbar(self):
        pass
    
    def load_preferences(self):
        # TODO: Figure out standard location for python apps to store prefs
        pass
    
    def save_preferences(self):
        pass
    
    # --------- MPL Events ---------
    
    def on_new_figure(self, figure, userdata=None): 
        self.main_frame.addSubWindow(figure)
        self.figures.append(figure)
        self.windowmenu.addAction(figure.activateAction())
    
    def on_destroy_figure(self, figure, userdata=None):
        if figure in self.figures:
            self.figures.remove(figure)  
        self.windowmenu.removeAction(figure.activateAction()) 
            
    # --------- End MPL Events ---------
  
  
    # --------- UI utility finctions ---------
  
    def add_action(self, key, label, callback, tip=None, icon=None, shortcut=None, userdata=None):
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
  
  
    # --------- Console functions ---------
  
    def _get_console_exec(self):
        return ""
        
    def _get_console_exports(self):
        return {'ui': self}
        
    def _get_console_config(self):
        return None
        
    def on_console_executing(self, source):
        pass
    
    def on_console_executed(self, response):
        pass
    
    def create_console(self):
            
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