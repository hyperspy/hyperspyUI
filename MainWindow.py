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

#import hyperspy.hspy
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
                        tip="Mirror navigation axes")
    
    def create_menu(self):
        mb = self.menuBar()
        
        # File menu (I/O)
        self.filemenu = mb.addMenu(tr("&File"))
        self.filemenu.addAction(self.actions['open'])
        self.filemenu.addAction(self.actions['close'])
        
        super(MainWindow, self).create_menu()
                        
    def create_toolbars(self):
        self.add_toolbar_button("Files", self.actions['open'])
        self.add_toolbar_button("Files", self.actions['close'])
        self.add_toolbar_button("Navigation", self.actions['mirror'])
        
        super(MainWindow, self).create_toolbars()
        
    def create_widgetbar(self):
        super(MainWindow, self).create_widgetbar()
        
        
    # ---------
    # Slots
    # ---------
            
    def mirror_navi(self, uisignals=None):
        # Select signals
        if uisignals is None:
            uisignals = self.sign_list.widget().get_selected()
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
            
    
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.showMaximized()
    app.exec_()
    
if __name__ == "__main__":
    main()