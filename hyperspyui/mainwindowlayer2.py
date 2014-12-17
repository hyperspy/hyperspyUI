# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 13:37:08 2014

@author: Vidar Tonaas Fauske
"""

import os, sys
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
import util

import hyperspy.hspy
import hyperspy.defaults_parser
from hyperspy.io_plugins import io_plugins

import uiprogressbar
uiprogressbar.takeover_progressbar()    # Enable hooks

glob_escape = re.compile(r'([\[\]])')


def get_accepted_extensions():
    extensions = set([ extensions.lower() for plugin in io_plugins 
                    for extensions in plugin.file_extensions])
    return extensions


class MainWindowLayer2(MainWindowLayer1):
    """
    Second layer in the application stack. Should integrate hyperspy basics,
    such as UI wrappings for hyperspy classes (Signal and Model), file I/O,
    etc.
    """
    
    def __init__(self, parent=None):        
        # Setup signals list. This is a BindingList, and all components of the
        # code that needs to keep track of the signals loaded bind into this.
        self.signals = BindingList()   
        
        # Setup variables
        self.progressbars = {} 
        
        super(MainWindowLayer2, self).__init__(parent)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Connect UIProgressBar for graphical hyperspy progress
        s = uiprogressbar.signaler
        s.connect(s, SIGNAL('created(int, int, QString)'),
                              self.on_progressbar_wanted)
        s.connect(s, SIGNAL('progress(int, int)'),
                              self.on_progressbar_update)
        s.connect(s, SIGNAL('progress(int, int, QString)'),
                              self.on_progressbar_update)
        s.connect(s, SIGNAL('finished_sig(int)'),
                              self.on_progressbar_finished)
        self.cancel_progressbar.connect(s.on_cancel)
        
        # Finish off hyperspy customization of layer 1
        self.setWindowTitle("HyperSpy")
        
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
        return sig
        
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
        s = self.tree.get_selected_signals()
        if len(s) < 1:
            w = self.main_frame.activeSubWindow()
            s = util.win2sig(w, self.figures)
        return s
        
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
        extensions = get_accepted_extensions()
        type_choices = ';;'.join(["*." + e for e in extensions])
        type_choices = ';;'.join(("All types (*.*)", type_choices))
                       
        if filenames is None:
            filenames = QFileDialog.getOpenFileNames(self,
                    tr('Load file'), self.cur_dir,
                    type_choices)
            if isinstance(filenames, tuple):    # Pyside returns tuple, PyQt not
                filenames = filenames[0]
            if not filenames:
                return False
            self.cur_dir = filenames[0]
            
        files_loaded = []
        for filename in filenames:    
            self.set_status("Loading \"" + filename + "\"...")
            self.setUpdatesEnabled(False)   # Prevent flickering during load
            try:
                escaped = glob_escape.sub(r'[\1]', filename)    # glob escapes
                sig = hyperspy.hspy.load(escaped)
                base = os.path.splitext( os.path.basename(filename) )[0]
                if isinstance(sig, list):
                    for s in sig:
                        self.add_signal_figure(s, base)
                else:
                    self.add_signal_figure(sig, base)
                files_loaded.append(filename)
            except (IOError, ValueError):
                self.set_status("Failed to load \"" + filename + "\"")
            finally:
                self.setUpdatesEnabled(True)    # Always resume updates!
                
        if len(files_loaded) == 1:
            self.set_status("Loaded \"" + files_loaded[0] + "\"")
        elif len(files_loaded) > 1:
            self.set_status("Loaded %d files" % len(files_loaded))
        return len(files_loaded) > 1
    
    def save(self, signals=None, filenames=None):
        if signals is None:
            signals = self.get_selected_signals()
            
        extensions = get_accepted_extensions()
        type_choices = ';;'.join(["*." + e for e in extensions])
        type_choices = ';;'.join(("All types (*.*)", type_choices))
            
        i = 0
        overwrite = None
        for s in signals:
            # Match signal to filename. If filenames has not been specified,
            # or there are no valid filename for curren signal index i, we
            # have to prompt the user.
            if filenames is None or len(filenames) <= i or filenames[i] is None:
                path_suggestion = self.get_signal_filepath_suggestion(s)
                filename = QFileDialog.getSaveFileName(self, tr("Save file"), 
                                            path_suggestion, type_choices,
                                            "All types (*.*)")[0]
                # Dialog should have prompted about overwrite
                overwrite = True
                if not filename:
                    continue
            else:
                filename = filenames[i]
                overwrite = None    # We need to confirm overwrites
            i += 1
            s.signal.save(filename, overwrite)
            
    def get_signal_filepath_suggestion(self, signal, deault_ext=None):
        if deault_ext is None:
            deault_ext = hyperspy.defaults_parser.preferences.General.default_file_format
         # Get initial suggestion for save dialog.  Use 
        # original_filename metadata if present, or self.cur_dir if not
        if signal.signal.metadata.has_item('General.original_filename'):
            f = signal.signal.metadata.General.original_filename
        else:
            f = self.cur_dir
        
        # Analyze suggested filename
        base, tail = os.path.split(f)
        fn, ext = os.path.splitext(tail)
        
        # If no directory in filename, use self.cur_dir's dirname
        if base is None or base == "":
            base = os.path.dirname(self.cur_dir)
        # If extension is not valid, use the defualt
        extensions = get_accepted_extensions()
        if ext not in extensions:
            ext = deault_ext
        # Filename itself is signal's name
        fn = signal.name
        # Build suggestion and return
        path_suggestion = os.path.sep.join((base, fn))
        path_suggestion = os.path.extsep.join((path_suggestion, ext))
        return path_suggestion
    
    # ---------- Drag and drop overloads ----------
    
    def dragEnterEvent(self, event):
        # Check file name extensions to see if we should accept
        extensions = set(get_accepted_extensions())
        mimeData = event.mimeData() 
        if mimeData.hasUrls():
            pathList = [url.toLocalFile() for url in mimeData.urls()]
            data_ext = set([os.path.splitext(p)[1][1:] for p in pathList])
            # Accept as long as we can read some of the files being dropped
            if 0 < len(data_ext.intersection(extensions)):
                event.acceptProposedAction()
    
#    def dragMoveEvent(event):
#        pass
#    
#    def dragLeaveEvent(event):
#        pass
    
    def dropEvent(self, event):
        # Something has been dropped. Try to load all file urls
        mimeData = event.mimeData()      
        if mimeData.hasUrls():
            pathList = [url.toLocalFile() for url in mimeData.urls()]
            if self.load(pathList):
                event.acceptProposedAction()
            
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
    
    # --------- Settings ---------
    
    def write_settings(self):
        super(MainWindowLayer2, self).write_settings()
        
    def read_settings(self):
        super(MainWindowLayer2, self).read_settings()

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
        ipcp = os.path.sep.join((os.path.dirname(__file__), "ipython_profile", 
                                 "ipython_embedded_config.py"))
        c = PyFileConfigLoader(ipcp).load_config()
        # ===== OR THIS =====
#        import hyperspy.Release        
#        from IPython.config import Config
#        c = Config()
#        c.FrontendWidget.banner = hyperspy.Release.info
        # ===== END =====
        return c