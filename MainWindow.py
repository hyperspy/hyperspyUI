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
        self.add_action("open", "&Open", self.load,
                        shortcut=QKeySequence.Open, 
                        tip="Open an existing file")
        
        self.add_action("mirror", "Mirror", self.mirror_navi,
                        tip="Mirror navigation axes")
                        
                        
    def create_toolbars(self):
        self.add_toolbar_button("Files", self.actions["open"])
        self.add_toolbar_button("Navigation", self.actions["mirror"])
        
    def create_widgetbar(self):
        # TODO: Default widgets? Brightness/contrast? YES
        s = SignalList()
        s.bind(self.signals)
        self.sign_list = self.add_widget(s)
        pass
        
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
    
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()