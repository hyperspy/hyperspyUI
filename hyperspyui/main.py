# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 02:10:29 2014

@author: Vidar Tonaas Fauske
"""

import sys
        
from python_qt_binding import QtGui, QtCore
    
def main():
    try:
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        app = QtGui.QApplication.instance()

    
    # Create and display the splash screen
    splash_pix = QtGui.QPixmap('../images/splash.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()    

    from mainwindow import MainWindow    
    
    form = MainWindow()
    form.showMaximized()
    
    splash.finish(form)
    
    app.exec_()
    
if __name__ == "__main__":
    main()