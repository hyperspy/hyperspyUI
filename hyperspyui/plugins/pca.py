# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 23:44:01 2014

@author: Vidar Tonaas Fauske
"""


import plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.util import win2sig, fig2win, Namespace
from hyperspyui.threaded import ProgressThreaded

def tr(text):
    return QCoreApplication.translate("PCA", text)

class PCA_Plugin(plugin.Plugin):
    def create_actions(self):
        self.ui.add_action('pca', "PCA", self.pca,
                        icon='pca.svg',
                        tip="Run Principal Component Analysis",
                        selection_callback=self.selection_rules)
    
    def create_menu(self):
        self.ui.signalmenu.addAction(self.ui.actions['pca'])
    
    def create_toolbars(self):
        self.ui.add_toolbar_button("Signal", self.ui.actions['pca'])
                  
    # --- Add PCA action ---
    def selection_rules(self, win, action):
        s = win2sig(win, self.ui.signals)
        if s is None or s.signal.data.ndim <= 1:
            action.setEnabled(False)
        else:
            action.setEnabled(True)
            
            
    def _get_signal(self, signal):
        if signal is None:
            signal = self.ui.get_selected_signal()
        s = signal.signal

        if s.data.dtype.char not in ['e', 'f', 'd']:  # If not float        
            mb = QMessageBox(QMessageBox.Information, tr("Convert or copy"), 
                             tr("Signal data has the wrong data type (float " + 
                             "needed). Would you like to convert the current" +
                             " signal, or perform the decomposition on a " +
                             "copy?"))
            convert = mb.addButton(tr("Convert"), QMessageBox.AcceptRole)
            copy = mb.addButton(tr("Copy"), QMessageBox.RejectRole)
            mb.addButton(QMessageBox.Cancel)
            mb.exec_()
            btn = mb.clickedButton()
            if btn not in (convert, copy):
                return
            elif btn == copy: 
                new_s = s.deepcopy()
                if s.data.ndim == 2:
                    bk_s_navigate = self.nav_dim_backups[s]
                    s.axes_manager._set_axis_attribute_values('navigate', 
                                                              bk_s_navigate)
                s = new_s
                self.ui.add_signal_figure(s, signal.name + "[float]")
            s.change_dtype(float)
        return s, signal
            
    def _do_decomposition(self, s, force=False):
        if s.data.ndim == 2:
            bk_s_navigate = \
                    s.axes_manager._get_axis_attribute_values('navigate')
            s.axes_manager.set_signal_dimension(1)
        
        if force or s.learning_results.explained_variance_ratio is None:
            s.decomposition()
        
        if s.data.ndim == 2:
            s.axes_manager._set_axis_attribute_values('navigate', 
                                                      bk_s_navigate)
        return s

    def pca(self, signal=None):
        ns = Namespace()
        ns.s, signal = self._get_signal(signal)
        
        def do_threaded():
            ns.s = self._do_decomposition(ns.s)
            
        def on_complete():
            ax = ns.s.plot_explained_variance_ratio()
                
            # Clean up plot and present, allow user to select components by picker
            ax.set_title("")
            scree = ax.get_figure().canvas
            scree.draw()
            scree.setWindowTitle("Pick number of components")
            def clicked(event):
                components = round(event.xdata)
                # Num comp. picked, perform PCA, wrap new signal and plot
                sc = ns.s.get_decomposition_model(components)
                self.ui.add_signal_figure(sc, signal.name + "[PCA]")
                # Close scree plot
                w = fig2win(scree.figure, self.ui.figures)
                w.close()
            scree.mpl_connect('button_press_event', clicked)
            
        t = ProgressThreaded(self.ui, do_threaded, on_complete, 
                             label="Performing PCA")
        t.run()
        
                        
                        
        
        