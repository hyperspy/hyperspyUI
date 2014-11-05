# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:46:35 2014

@author: vidarton
"""

import sys
    
from MainWindowLayer2 import MainWindowLayer2   # Should go before any MPL imports

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)

import hyperspy.components
import hyperspy.utils.plot


# TODO: Add Model UI wrapper
# TODO: Can we keep console as well as Signal List? Revert back to Close = Hide?

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
        # TODO: Set from preferences?, default to working dir (can be 
        # customized by modifying launcher)
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
        
        compnames = ['Arctan', 'Bleasdale', 'DoubleOffset', 'DoublePowerLaw', 
                     'Erf', 'Exponential', 'Gaussian', 'Logistic',
                     'Lorentzian', 'Offset', 'PowerLaw', 'SEE', 'RC', 
                     'Vignetting', 'Voigt', 'Polynomial', 'PESCoreLineShape', 
                     'VolumePlasmonDrude']     
        self.comp_actions = []
        for name in compnames:
            t = getattr(hyperspy.components, name)
            ac_name = 'add_component_' + name
            def f():
                self.make_component(t)
            self.add_action(ac_name, name, f, 
                            tip="Add a component of type " + name)
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
            # the navigators. To keep UI from flickering, we suspend updates
            # and SignalUIWrapper saves and then restores window geometry
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
        if uisignals is None:
            uisignals = self.sign_list.widget().get_selected()
        for s in uisignals:
            s.close()
            
    def make_component(self, comp_type):
        # TODO: Get model
        m
        
        m.add_component(comp_type)
            
    
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.showMaximized()
    app.exec_()
    
if __name__ == "__main__":
    main()