# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:46:35 2014

@author: vidarton
"""

import sys
#from functools import partial
    
from mainwindowlayer2 import MainWindowLayer2   # Should go before any MPL imports

from util import create_add_component_actions, fig2win, win2sig
from signalwrapper import SignalWrapper
from signallist import SignalList
from threaded import ProgressThread
from contrastwidget import ContrastWidget

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)

import hyperspy.utils.plot


class Namespace: pass

class MainWindow(MainWindowLayer2):
    """
    Main window of the application. Top layer in application stack. Is 
    responsible for adding default actions, and filling the menus and toolbars.
    Also creates the default widgets. Any button-actions should also be 
    accessible as a slot, such that other things can connect into it, and so
    that it is accessible from the console's 'ui' variable.
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowIcon(QIcon('../images/hyperspy_logo.png'))
        # TODO: Set from preferences?, default to working dir (can be 
        # customized by modifying launcher)
#        self.cur_dir = "D:/NetSync/TEM/20140304 - NWG130/SI-001/Spectrum Imaging-005"
        self.cur_dir = "D:/NetSync/TEM/20140214 - NWG130 refibbed/EELS_02_Map/Spectrum Imaging-001/"
          
        
    def create_default_actions(self):       
        super(MainWindow, self).create_default_actions()
        
        self.add_action('open', "&Open", self.load,
                        shortcut=QKeySequence.Open, 
                        icon='../images/open.svg',
                        tip="Open existing file(s)")
        self.add_action('close', "&Close", self.close_signal,
                        shortcut=QKeySequence.Close, 
                        icon='../images/close_window.svg',
                        tip="Close the selected signal(s)")
        
        self.add_action('mirror', "Mirror", self.mirror_navi,
                        icon='../images/mirror.svg',
                        tip="Mirror navigation axes of selected signals")
        
        self.add_action('add_model', "Create Model", self.make_model,
                        tip="Create a model for the selected signal")
                        
        self.add_action('fourier_ratio', "Foruier Ratio Deconvoloution",
                        self.fourier_ratio, 
                        icon='../images/fourier_ratio.svg',
                        tip="Use the Fourier-Ratio method" +
                        " to deconvolve one signal from another")
                        
        self.add_action('remove_background', "Remove Background",
                        self.remove_background, 
                        icon='../images/power_law.svg',
                        tip="Interactively define the background, and remove it")
                        
        def pca_selection_rules(win, action):
            s = win2sig(win, self.signals)
            if s is None or s.signal.axes_manager.navigation_dimension < 1:
                action.setEnabled(False)
            else:
                action.setEnabled(True)
                
        self.add_action('pca', "PCA", self.pca,
                        icon='../images/pca.svg',
                        tip="Run Principal Component Analysis",
                        selection_callback=pca_selection_rules)
        self.actions['pca'].setEnabled(False)   # Need valid signal to be enabled
                        
        # TODO: Set signal type action (EDS TEM etc.)
        # TODO: Set signal datatype
        
        comp_actions = create_add_component_actions(self, self.make_component)
        self.comp_actions = []
        for ac_name, ac in comp_actions.iteritems():
            self.actions[ac_name] = ac
            self.comp_actions.append(ac_name)
    
    def create_menu(self):
        mb = self.menuBar()
        
        # File menu (I/O)
        self.filemenu = mb.addMenu(tr("&File"))
        self.filemenu.addAction(self.actions['open'])
        self.filemenu.addAction(self.actions['close'])
        
        # Signal menu
        self.signalmenu = mb.addMenu(tr("&Signal"))
        self.signalmenu.addAction(self.actions['mirror'])
        self.signalmenu.addAction(self.actions['remove_background'])
        self.signalmenu.addAction(self.actions['pca'])
        
        # Model menu
        self.modelmenu = mb.addMenu(tr("&Model"))
        self.modelmenu.addAction(self.actions['add_model'])
        self.modelmenu_sep1 = self.modelmenu.addSeparator()
        
        self.componentmenu = self.modelmenu.addMenu(tr("&Add Component"))
        for acname in self.comp_actions:
            self.componentmenu.addAction(self.actions[acname])

        # Create Windows menu        
        super(MainWindow, self).create_menu()
        
                        
    def create_toolbars(self):
        self.add_toolbar_button("Files", self.actions['open'])
        self.add_toolbar_button("Files", self.actions['close'])
        self.add_toolbar_button("Signal", self.actions['mirror'])
        self.add_toolbar_button("Signal", self.actions['remove_background'])
        self.add_toolbar_button("Signal", self.actions['fourier_ratio'])
        self.add_toolbar_button("Signal", self.actions['pca'])
        
        super(MainWindow, self).create_toolbars()
        
    def create_widgetbar(self):
        super(MainWindow, self).create_widgetbar()
        
        cbw = ContrastWidget(self)
        self.main_frame.subWindowActivated.connect(cbw.on_figure_change)
        self.add_widget(cbw)
        
    # ---------
    # Slots
    # ---------
            
    def mirror_navi(self, uisignals=None):
        # Select signals
        if uisignals is None:
            uisignals = self.get_selected_signals()
        if len(uisignals) > 1:
            signals = [s.signal for s in uisignals]
            
            # hyperspy closes, and then recreates figures when mirroring 
            # the navigators. To keep UI from flickering, we suspend updates.
            # SignalWrapper also saves and then restores window geometry
            self.setUpdatesEnabled(False)
            try:
                for s in uisignals:
                    s.keep_on_close = True
                hyperspy.utils.plot.plot_signals(signals)
                for s in uisignals:
                    s.update_figures()
                    s.keep_on_close = False
            finally:
                self.setUpdatesEnabled(True)    # Continue updating UI
        else:
            mb = QMessageBox(QMessageBox.Information, tr("Select two or more"), 
                             tr("You need to select two or more signals" + 
                             " to mirror"), QMessageBox.Ok)
            mb.exec_()
            
    def close_signal(self, uisignals=None):
        uisignals = self.get_selected_signals()
        for s in uisignals:
            s.close()
            
    def fourier_ratio(self):
        wrap = QWidget(self)
        pickerCL = SignalList(self.signals, wrap, False)
        pickerLL = SignalList(self.signals, wrap, False)
        grid = QGridLayout(wrap)
        grid.addWidget(QLabel(tr("Core loss")), 1, 1)
        grid.addWidget(QLabel(tr("Low loss")), 1, 2)
        grid.addWidget(pickerCL, 2, 1)
        grid.addWidget(pickerLL, 2, 2)
        wrap.setLayout(grid)
        
        diag = self.show_okcancel_dialog("Select signals", wrap, True)
        
        if diag.result() == QDialog.Accepted:
            s_core = pickerCL.get_selected()
            s_lowloss = pickerLL.get_selected()
            
            # Variable to store return value in
            ns = Namespace()
            ns.s_return = None
            
#            s_core.signal.remove_background()
            def run_fr():
                ns.s_return = s_core.signal.fourier_ratio_deconvolution(
                                                            s_lowloss.signal)
            def fr_complete():
                title = s_core.name + "[Fourier-ratio]" 
                self.add_signal_figures(ns.s_return, title)
                
            t = ProgressThread(self, run_fr, fr_complete, 
                               "Performing Fourier-ratio deconvolution")
            t.run()
        pickerCL.unbind(self.signals)
        pickerLL.unbind(self.signals)
        
    def remove_background(self, signal=None):
        if signal is None:
            signal = self.get_selected_signal()
        signal.run_nonblock(signal.signal.remove_background, "Background removal tool")


    def pca(self, signal=None):
        if signal is None:
            signal = self.get_selected_signal()
        signal.signal.decomposition()
        ax = signal.signal.plot_explained_variance_ratio()
        ax.set_title("")
        spree = ax.get_figure().canvas
        spree.draw()
        spree.setWindowTitle("Pick number of components")
        def clicked(event):
            components = round(event.xdata)
            sc = signal.signal.get_decomposition_model(components)
            scw = SignalWrapper(sc, self, signal.name + "[PCA]")
            self.signals.append(scw)
            w = fig2win(spree.figure, self.figures)
            w.close()
        spree.mpl_connect('button_press_event', clicked)
            
    
def main():
    app = QApplication(sys.argv)

    
    # Create and display the splash screen
#    splash_pix = QPixmap('splash_loading.png')
#    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
#    splash.setMask(splash_pix.mask())
#    splash.show()
#    app.processEvents()    
    
    form = MainWindow()
    form.showMaximized()
    
#    splash.finish(form)
    
    app.exec_()
    
if __name__ == "__main__":
    main()