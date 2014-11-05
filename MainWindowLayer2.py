# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 13:37:08 2014

@author: vidarton
"""

import os

# Hyperspy uses traitsui, set proper backend
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

from MainWindowLayer1 import MainWindowLayer1, tr

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from SignalUIWrapper import SignalUIWrapper
from BindingList import BindingList
from SignalList import SignalList
from ModelWrapper import ModelWrapper

import hyperspy.hspy



class MainWindowLayer2(MainWindowLayer1):
    """
    Second layer in the application stack. Should integrate hyperspy basics,
    such as UI wrappings for hyperspy classes (Signal and Model), file I/O,
    etc.
    """
    
    def __init__(self, parent=None):        
        self.signals = BindingList()
        
        super(MainWindowLayer2, self).__init__(parent)
            
        self.cur_dir = ""
        
        self.setWindowTitle("HyperSpy")
        self.set_status("Ready")
        
    def create_widgetbar(self):  
        super(MainWindowLayer2, self).create_widgetbar() 
        
        # TODO: Default widgets? Brightness/contrast? YES
        s = SignalList()
        s.setWindowTitle(tr("Signal Select"))
        s.bind(self.signals)
        self.sign_list = self.add_widget(s)
        
        
    def create_menu(self):
        # Super creates Windows menu
        super(MainWindowLayer2, self).create_menu()       
        
        # Add custom action to signals' BindingList, so appropriate menu items 
        # are removed if a signal is removed from the list
        def rem_s(value):
            for f in value.figures:
                self.windowmenu.removeAction(f.activateAction())
        self.signals.add_custom(self.windowmenu, None, None, None, 
                                rem_s, lambda i: rem_s(self.signals[i]))
    
    def add_signal_figures(self, signal, sig_name=None):
        sig = SignalUIWrapper(signal, self, sig_name)
        self.signals.append(sig)
        
    def add_model(self, signal, *args, **kwargs):
        m = hyperspy.hspy.create_model(signal, *args, **kwargs)
        uis = [s for s in self.signals if s.signal == signal]
        mw = ModelWrapper(m, uis[0])
        uis[0].add_model(mw)
        return m
        
        
    # --------- File I/O ----------
        
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
            self.setUpdatesEnabled(False)   # Prevent flickering during load
            sig = hyperspy.hspy.load(filename)
            base = os.path.splitext( os.path.basename(filename) )[0]
            self.add_signal_figures(sig, base)
            self.setUpdatesEnabled(True)
        if len(filenames) == 1:
            self.set_status("Loaded \"" + filenames[0] + "\"")
        elif len(filenames) > 1:
            self.set_status("Loaded %d files" % len(filenames))
        

    # --------- Console functions ----------    

    def on_console_executing(self, source):
        super(MainWindowLayer2, self).on_console_executing(source)
#        self.setUpdatesEnabled(False)
        for s in self.signals:
            s.keep_on_close = True
        
    def on_console_executed(self, response):
#        print response
        super(MainWindowLayer2, self).on_console_executed(response)
        for s in self.signals:
            s.update_figures()
            s.keep_on_close = False
#        self.setUpdatesEnabled(True)
    
    def _get_console_exec(self):
        ex = super(MainWindowLayer2, self)._get_console_exec()
        ex += '\nfrom hyperspy.hspy import *'
        return ex
        
    def _get_console_exports(self):
        push = super(MainWindowLayer2, self)._get_console_exports()
        push['signals'] = self.signals
        push['create_model'] = self.add_model    # Override hyperspy.hspy.create_model
        return push
        
    def _get_console_config(self):
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
        return c