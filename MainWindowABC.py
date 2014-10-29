# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 21:17:42 2014

@author: vidarton
"""


import os

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)

# Imports for in-app console
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


from FigureManager import FigureManager
from SignalUIWrapper import SignalUIWrapper
from BindingList import BindingList

import hyperspy.hspy


class MainWindowABC(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindowABC, self).__init__(parent)
        
        # Properties
        self.toolbar_button_unit = 32   #TODO: Make a property
        self.FIGURE_SIZE = (512, 512)
        self.cur_dir = ""
        self.default_fig_floating = False
        self.default_widget_floating = False
        
        # Collections
        self.widgets = []   # Widgets in widget bar
        self.actions = {}
        self.toolbars = {}
        self.menus = {}
        self.signals = BindingList()
        
        self.create_ui()
        
    def create_ui(self):
        self.main_frame = QWidget()

        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
#        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

        self.create_default_actions()   # Goes before menu/toolbar/widgetbar
        
        self.create_console()   # Needs to go before menu
        self.create_menu()  # This needs to happen before the widgetbar and console
        self.create_toolbars()
        self.create_widgetbar()
        
        self.create_figure_manager()
        
#        self.main_frame.setLayout()
        self.setCentralWidget(self.main_frame)
        self.setWindowTitle("HyperSpy")
        self.set_status("Ready")
        
    def create_default_actions(self):
        raise NotImplementedError()
    
    def create_menu(self):
         # TODO: Do we need a menu manager class?
        raise NotImplementedError()
    
    def create_figure_manager(self):
        self.fig_mgr = FigureManager.Instance()

        # TODO: Individual control, or all/none? DM says all float, Adobe All/None (in windows), ImageJ All float

    
    def create_toolbars(self):
        raise NotImplementedError()
    
    def set_status(self, msg):
        # TODO: What info is needed? Add simple label first, create utility to add more?
        self.statusBar().showMessage(msg)
    
    def create_widgetbar(self):
        raise NotImplementedError()
    
    def load_preferences(self):
        # TODO: Figure out standard location for python apps to store prefs
        pass
    
    def save_preferences(self):
        pass
    
    
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
        
    
    def add_menuitem(self): # TODO: Figure out reasonable API for nesting
        pass
    
    def add_widget(self, widget):
        d = QDockWidget(self)
        d.setWidget(widget)
        d.setWindowTitle(widget.windowTitle())
        d.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea) 
        self.addDockWidget(Qt.RightDockWidgetArea, d)
        d.setFloating(self.default_widget_floating)
        return d
        
    def add_figure(self, figure):
        figure.setAllowedAreas(Qt.TopDockWidgetArea) 
        self.addDockWidget(Qt.TopDockWidgetArea, figure)
        figure.setFloating(self.default_fig_floating)
        figure.draw()
        self.fig_mgr.add(figure)
        
    
    def add_signal_figures(self, signal, sig_name=None):
        sig = SignalUIWrapper(signal, self, sig_name)
        for f in sig.figures:
            self.add_figure(f)
        self.signals.append(sig)
            
    
    def create_console(self):
        # Create an in-process kernel
        app = guisupport.get_app_qt4()
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        
        # Set the kernel data
        kernel = kernel_manager.kernel
        kernel.gui = 'qt4'
        
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        
        # This is where we push variables to the console
        kernel.shell.ex('from hyperspy.hspy import *')
        kernel.shell.push({'ui': self, 'signals': self.signals})
    
        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            app.exit()  # TODO: Really?
            
            
        # ===== THIS ======
        from IPython.config.loader import PyFileConfigLoader
        from hyperspy import __file__ as hf
        ipcp = os.path.dirname(hf) + os.path.sep + "ipython_profile" + os.path.sep
        c = PyFileConfigLoader(ipcp + "ipython_embedded_config.py").load_config()
        # ===== OR THIS =====
#        import hyperspy.Release        
#        from IPython.config import Config
#        c = Config()
#        c.FrontendWidget.banner = hyperspy.Release.info
        # ===== END =====
        control = RichIPythonWidget(config=c)
        control.kernel_manager = kernel_manager    
        control.kernel_client = kernel_client
        control.exit_requested.connect(stop)
        self.console = control

        self._console_dock = QDockWidget()
        self._console_dock.setWidget(control)
        self._console_dock.setWindowTitle("Console")
        self.addDockWidget(Qt.BottomDockWidgetArea, self._console_dock)
        
        
    def load(self, filenames=None):
        if filenames is None:
            file_choices = "DM (*.dm3;*.dm4)"
            filenames = QFileDialog.getOpenFileNames(self,
                    tr('Load file'), self.cur_dir,
                    file_choices)
            if not filenames:
                return
#            print filenames
#            self.cur_dir = os.path.dirname(filenames)
            self.cur_dir = filenames[0]
#        print "hpy"
        for filename in filenames:    
            self.set_status("Loading \"" + filename + "\"...")
            sig = hyperspy.hspy.load(filename)
            base = os.path.splitext( os.path.basename(filename) )[0]
            self.add_signal_figures(sig, base)
        if len(filenames) == 1:
            self.set_status("Loaded \"" + filenames[0] + "\"")
        elif len(filenames) > 1:
            self.set_status("Loaded %d files" % len(filenames))