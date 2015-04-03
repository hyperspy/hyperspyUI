# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 02:10:29 2014

@author: Vidar Tonaas Fauske
"""

import os
import sys

from python_qt_binding import QtGui, QtCore
import info
from singleapplication import get_app


# TODO: Disable recording on EditorWidget's run()
# TODO: Expose direct hyperspy signals collection.
# TODO: On plugin creation, scroll view to top, or at least so bottoms line up
# TODO: Pluign name --> sanitize on creation in Editor
# TODO: DataView window management: Dblclick activates/minimize, possibly have
#       separate management buttons up front.
# TODO: ContrastWidget: Have B/C enabled when on auto, and turn off auto on edit.
# TODO: Autohide toolbars w.r.t. signal type.
# TODO: Add selection groups for signals by hierarchy in DataViewWidget
# TODO: Navigation coords for active signal in statusbar (strip from fig)
# TODO: Mouse coords (pixels & units) in statusbar
# TODO: Crop + others record code


def main():
    exe_dir, exe_name = os.path.split(sys.executable)
    if exe_name.startswith('pythonw'):
        sys.stdout = sys.stderr = open(
            os.path.dirname(__file__) + '/../hyperspyui.log', 'w')
    # TODO: Make single/multi a setting
    app = get_app('hyperspyui')     # Make sure we only have a single instance

    QtCore.QCoreApplication.setApplicationName("HyperSpyUI")
    QtCore.QCoreApplication.setOrganizationName("Hyperspy")
    QtCore.QCoreApplication.setApplicationVersion(info.version)

    # Create and display the splash screen
    splash_pix = QtGui.QPixmap(
        os.path.dirname(__file__) + '/../images/splash.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    from mainwindow import MainWindow

    form = MainWindow()
    app.messageAvailable.connect(form.handleSecondInstance)
    form.showMaximized()

    splash.finish(form)

    app.exec_()

if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__) + '/../')
    main()
