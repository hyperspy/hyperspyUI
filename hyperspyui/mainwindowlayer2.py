# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 13:37:08 2014

@author: Vidar Tonaas Fauske
"""

import os
import re

# Hyperspy uses traitsui, set proper backend
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

from mainwindowlayer1 import MainWindowLayer1, tr

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from signalwrapper import SignalWrapper
from bindinglist import BindingList
from dataviewwidget import DataViewWidget

import hyperspy.hspy
import hyperspy.defaults_parser
from hyperspy.io_plugins import io_plugins

import uiprogressbar
uiprogressbar.takeover_progressbar()    # Enable hooks

glob_escape = re.compile(r'([\[\]])')


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
        self.progressbars = {}
        
        s = uiprogressbar.signaler
        s.connect(s, SIGNAL('created(int, int, QString)'),
                              self.on_progressbar_wanted)
        s.connect(s, SIGNAL('progress(int, int)'),
                              self.on_progressbar_update)
        s.connect(s, SIGNAL('progress(int, int, QString)'),
                              self.on_progressbar_update)
        s.connect(s, SIGNAL('finished_sig(int)'),
                              self.on_progressbar_finished)
        self.cancel_progressbar.connect(s.cancel)
        
        self.setWindowTitle("HyperSpy")
        self.set_status("Ready")
        
    def create_widgetbar(self):  
        super(MainWindowLayer2, self).create_widgetbar() 
        
        self.tree = DataViewWidget(self, self)
        self.tree.setWindowTitle(tr("Data View"))
        # Sync tree with signals list:
        self.signals.add_custom(self.tree, self.tree.add_signal, None,
                                None, self.tree.remove, None)
        self.main_frame.subWindowActivated.connect(self.tree.on_mdiwin_activated)
        self.add_widget(self.tree)
        
        
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
    
    def add_signal_figure(self, signal, sig_name=None):
        sig = SignalWrapper(signal, self, sig_name)
        self.signals.append(sig)
        # Little hack to activate after creation
        self.main_frame.subWindowActivated.emit(self.main_frame.activeSubWindow())
        
    def add_model(self, signal, *args, **kwargs):
        """
        Add a default model for the given/selected signal. Returns the 
        newly created ModelWrapper.
        """
        if signal is None:
            signal = self.get_selected_signal()
        elif not isinstance(signal, SignalWrapper):
            signal = [s for s in self.signals if s.signal == signal]
            signal = signal[0]
        mw = signal.make_model(*args, **kwargs)
        return mw
        
    def make_model(self, signal=None, *args, **kwargs):
        """
        Same as add_model(), but returns the hyperspy.Model instead of the 
        wrapper.
        """
        mw = self.add_model(signal, *args, **kwargs)
        return mw.model
            
    def make_component(self, comp_type):
        m = self.get_selected_model()       
        m.add_component(comp_type)
        
    
    # -------- Selection management -------
        
    def get_selected_signal(self, error_on_multiple=False):
        signals = self.get_selected_signals()
        if len(signals) < 1:
            return None
        elif error_on_multiple and len(signals) > 1:
            mb = QMessageBox(QMessageBox.Information, tr("Select one signal only"), 
                             tr("You can only select one signal at the time" + 
                             " for this function. Currently, several are selected"),
                             QMessageBox.Ok)
            mb.exec_()
        return signals[0]
        
    def get_selected_signals(self):
        return self.tree.get_selected_signals()
        
    def get_selected_model(self):
        return self.tree.get_selected_model()
        
    def get_selected_component(self):
        return self.tree.get_selected_component()
        
        
    # --------- File I/O ----------
        
    def load(self, filenames=None):
        """
        Load 'filenames', or if 'filenames' is None, open a dialog to let the
        user interactively browse for files. It then load these files using
        hyperspy.hspy.load and wraps them and adds them to self.signals.
        """
        extensions = set([ extensions.lower() for plugin in io_plugins 
                        for extensions in plugin.file_extensions])
        type_choices = ';;'.join(["*." + e for e in extensions])
        type_choices = ';;'.join(("All types (*.*)", type_choices))
                            
        if filenames is None:
            filenames = QFileDialog.getOpenFileNames(self,
                    tr('Load file'), self.cur_dir,
                    type_choices)
            if isinstance(filenames, tuple):    # Pyside/PyQt are different
                filenames = filenames[0]
            if not filenames:
                return
#            self.cur_dir = os.path.dirname(filenames)
            self.cur_dir = filenames[0]
        for filename in filenames:    
            self.set_status("Loading \"" + filename + "\"...")
            self.setUpdatesEnabled(False)   # Prevent flickering during load
            try:
                escaped = glob_escape.sub(r'[\1]', filename)    # glob escapes
                sig = hyperspy.hspy.load(escaped)
                base = os.path.splitext( os.path.basename(filename) )[0]
                self.add_signal_figure(sig, base)
            finally:
                self.setUpdatesEnabled(True)
        if len(filenames) == 1:
            self.set_status("Loaded \"" + filenames[0] + "\"")
        elif len(filenames) > 1:
            self.set_status("Loaded %d files" % len(filenames))
    
    def save(self, signals=None, filenames=None):
        if signals is None:
            signals = self.get_selected_signals()
            
        extensions = set([ extensions.lower() for plugin in io_plugins 
                        for extensions in plugin.file_extensions])
        type_choices = ';;'.join(["*." + e for e in extensions])
        type_choices = ';;'.join(("All types (*.*)", type_choices))
        deault_ext = hyperspy.defaults_parser.preferences.General.default_file_format
            
        i = 0
        overwrite = None
        for s in signals:
            if filenames is None or len(filenames) <= i or filenames[i] is None:
                if s.signal.metadata.has_item('General.original_filename'):
                    f = s.signal.metadata.General.original_filename
                else:
                    f = self.cur_dir
                base, tail = os.path.split(f)
                fn, ext = os.path.splitext(tail)
                if base is None or base == "":
                    base = os.path.dirname(self.cur_dir)
                if ext not in extensions:
                    ext = deault_ext
                fn = s.name
                path_suggestion = os.path.sep.join((base, fn))
                path_suggestion = os.path.extsep.join((path_suggestion, ext))
                filename = QFileDialog.getSaveFileName(self, tr("Save file"), 
                                            path_suggestion, type_choices,
                                            "All types (*.*)")[0]
                overwrite = True
                if not filename:
                    return
            else:
                filename = filenames[i]
                overwrite = None
            i += 1
            s.signal.save(filename, overwrite)
                
            
    # --------- Hyperspy progress bars ----------
        
    cancel_progressbar = Signal(int)
            
    def on_progressbar_wanted(self, pid, maxval, label):
        progressbar = QProgressDialog(self)
        progressbar.setMinimumDuration(2000)
        progressbar.setMinimum(0)
        progressbar.setMaximum(maxval)
        progressbar.setWindowTitle("Processing")
        progressbar.setLabelText(label)
        
        def cancel():
            self.cancel_progressbar.emit(pid)
        progressbar.canceled.connect(cancel)
        progressbar.setWindowModality(Qt.WindowModal)
        
        self.progressbars[pid] = progressbar
        
    def on_progressbar_update(self, pid, value, txt=None):
        if pid not in self.progressbars:
            return
        self.progressbars[pid].setValue(value)
        if txt is not None:
            self.progressbars[pid].setLabelText(txt) 
        
    def on_progressbar_finished(self, pid):
        progressbar = self.progressbars.pop(pid)
        progressbar.close()
    
    # --------- End hyperspy progress bars ----------

    # --------- Console functions ----------    

    def on_console_executing(self, source):
        super(MainWindowLayer2, self).on_console_executing(source)
#        self.setUpdatesEnabled(False)
        for s in self.signals:
            s.keep_on_close = True
        
    def on_console_executed(self, response):
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
        push['create_model'] = self.make_model    # Override hyperspy.hspy.create_model
        return push
        
    def _get_console_config(self):
        # ===== THIS ======
        from IPython.config.loader import PyFileConfigLoader
        ipcp = os.path.sep.join(("ipython_profile", "ipython_embedded_config.py"))
        c = PyFileConfigLoader(ipcp).load_config()
        # ===== OR THIS =====
#        import hyperspy.Release        
#        from IPython.config import Config
#        c = Config()
#        c.FrontendWidget.banner = hyperspy.Release.info
        # ===== END =====
        return c