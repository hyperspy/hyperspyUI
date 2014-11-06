# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:46:35 2014

@author: vidarton
"""

import sys
#from functools import partial
    
from MainWindowLayer2 import MainWindowLayer2   # Should go before any MPL imports
from util import create_add_component_actions
from SignalList import SignalList
from SignalUIWrapper import SignalUIWrapper

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)

import hyperspy.utils.plot



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
        self.setWindowIcon(QIcon('images/hyperspy_logo.png'))
        # TODO: Set from preferences?, default to working dir (can be 
        # customized by modifying launcher)
#        self.cur_dir = "D:/NetSync/TEM/20140304 - NWG130/SI-001/Spectrum Imaging-005"
        self.cur_dir = "D:/NetSync/TEM/20140214 - NWG130 refibbed/EELS_02_Map/Spectrum Imaging-001/"
          
        
    def create_default_actions(self):       
        super(MainWindow, self).create_default_actions()
        
        self.add_action('open', "&Open", self.load,
                        shortcut=QKeySequence.Open, 
                        tip="Open an existing file")
        self.add_action('close', "&Close", self.close_signal,
                        shortcut=QKeySequence.Close, 
                        tip="Close the selected signal")
        
        self.add_action('mirror', "Mirror", self.mirror_navi,
                        tip="Mirror navigation axes of selected signals")
        
        self.add_action('add_model', "Create Model", self.make_model,
                        tip="Create a model for the selected signal")
                        
        self.add_action('fourier_ratio', "Foruier Ratio Deconvoloution",
                        self.fourier_ratio, tip="Use the Fourier Ratio method" +
                        " to deconvolve one signal from another")
                        
        self.add_action('remove_background', "Remove Background",
                        self.remove_background, 
                        tip="Interactively define the background, and remove it")
                        
        self.add_action('pca', "PCA", self.pca,
                        tip="Run Principal Component Analysis")
        
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
            # SignalUIWrapper also saves and then restores window geometry
            self.setUpdatesEnabled(False)
            for s in uisignals:
                s.keep_on_close = True
            hyperspy.utils.plot.plot_signals(signals)
            for s in uisignals:
                s.update_figures()
                s.keep_on_close = False
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
            
#            s_core.signal.remove_background()
            s_core.signal.fourier_ratio_deconvolution(s_lowloss.signal)
            s_core.plot()
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
            scw = SignalUIWrapper(sc, self, signal.name + "[PCA]")
            self.signals.append(scw)
            spree.close()
        spree.mpl_connect('button_press_event', clicked)
        # TODO: Auto, or ask for n components, or use picker
            
    
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.showMaximized()
    app.exec_()
    
if __name__ == "__main__":
    main()