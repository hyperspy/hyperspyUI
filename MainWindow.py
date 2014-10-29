# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:46:35 2014

@author: vidarton
"""

import sys
from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

def tr(text):
    return QCoreApplication.translate("MainWindow", text)
    
import matplotlib
matplotlib.use('Qt4Agg')

#import hyperspy.hspy
import hyperspy.utils.plot

from MainWindowABC import MainWindowABC
from SignalList import SignalList

class MainWindow(MainWindowABC):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.cur_dir = "D:/NetSync/TEM/20140214 - NWG130 refibbed/EELS_02_Map/Spectrum Imaging-001/"
        
        
        
    def create_default_actions(self):
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
        filemenu = mb.addMenu(tr("&File"))
        filemenu.addAction(self.actions['open'])
        filemenu.addAction(self.actions['close'])
        
        # Window menu is filled in add_widget and add_figure
        self.windowmenu = mb.addMenu(tr("&Windows"))
        self.windowmenu.addAction(self._console_dock.toggleViewAction())
        self.windowmenu_sep = self.windowmenu.addSeparator()
                        
    def create_toolbars(self):
        self.add_toolbar_button("Files", self.actions['open'])
        self.add_toolbar_button("Files", self.actions['close'])
        self.add_toolbar_button("Navigation", self.actions['mirror'])
        
    def create_widgetbar(self):
        # TODO: Default widgets? Brightness/contrast? YES
        s = SignalList()
        s.setWindowTitle(tr("Signal Select"))
        s.bind(self.signals)
        self.sign_list = self.add_widget(s)
        
    def add_widget(self, widget):
        d = super(MainWindow, self).add_widget(widget)
        # Insert widgets before separator (figures are after)
        self.windowmenu.insertAction(self.windowmenu_sep, d.toggleViewAction())
        return d
        
    def add_figure(self, figure):
        ret = super(MainWindow, self).add_figure(figure)
        self.windowmenu.addAction(figure.toggleViewAction())
        return ret  # No know ret object now, but doesn\t hurt to have it
        
        
    # ---------
    # Slots
    # ---------
            
    def mirror_navi(self):
        # Select signals
        uisignals = self.sign_list.widget().get_selected()
        if len(uisignals) > 1:
            signals = [s.signal for s in uisignals]
            hyperspy.utils.plot.plot_signals(signals)
            for s in uisignals:
                s.update_figures()
        else:
            mb = QMessageBox(QMessageBox.Information, tr("Select two or more"), 
                             tr("You need to select two or more signals" + 
                             " to mirror"), QMessageBox.Ok)
            mb.exec_()
            
    def close_signal(self):
        uisignals = self.sign_list.widget().get_selected()
        for s in uisignals:
            s.close()
            self.signals.remove(s)
            
    
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()