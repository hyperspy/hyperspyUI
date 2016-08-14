# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Tue Nov 25 02:10:29 2014

@author: Vidar Tonaas Fauske
"""

import os
import sys
import locale

# TODO: Make sure tools are disconnected when closing signal!

# TODO: Autohide toolbars w.r.t. signal type. (maybe?)
# TODO: Add selection groups for signals by hierarchy in DataViewWidget
# TODO: Make sure everything records / plays back code
# TODO: MPL artist editor via traitsui with custom handler
# TODO: Batch processing dialog (browse + drop&drop target)
# TODO: Editor utils: threading + parallell processing (w/batch input)
# TODO: Add xray 3rd state: Element present, but not used for maps
# TODO: Add xray background window tool for modifying those by auto
# TODO: Add quantification button. Needs k-factor setup.
# TODO: Create contributed plugins repository with UI integrated hot-load
# TODO: Auto-resize font in Periodic table
# TODO: Utilities to combine signals into stack and reverse
# TODO: Make editor tabs drag&droppable + default to all in one
# TODO: Make data type changer handle RGBX data types.
# TODO: Metadata explorer (TreeView)
# TODO: Variable explorer (Signal/Model etc.). 3rd party library?
# TODO: Disable tools when no figure


import logging
logging.basicConfig()
logging.getLogger('hyperspy').setLevel(logging.DEBUG)
logging.getLogger('hyperspyui').setLevel(logging.DEBUG)


def _get_logfile():
    _, exe_name = os.path.split(sys.executable)
    if exe_name.startswith('pythonw'):
        log_path = os.path.dirname(__file__) + '/hyperspyui.log'
        try:
            log_file = open(log_path, 'w')
        except IOError:
            log_path = os.path.expanduser('~/hyperspyui.log')
            try:
                log_file = open(log_path, 'w')
            except IOError:
                log_file = None     # No log file for us!
    else:
        log_file = None
    return log_file


def main():
    from python_qt_binding import QtGui, QtCore, QT_BINDING
    import hyperspyui.info
    from hyperspyui.singleapplication import get_app
    from hyperspyui.settings import Settings
    from hyperspyui.util import dummy_context_manager

    # Need to set early to make QSettings accessible
    QtCore.QCoreApplication.setApplicationName("HyperSpyUI")
    QtCore.QCoreApplication.setOrganizationName("Hyperspy")
    QtCore.QCoreApplication.setApplicationVersion(hyperspyui.info.version)

    # First, clear all default settings!
    Settings.clear_defaults()
    # Setup default for single/multi-instance
    settings = Settings(group="General")
    settings.set_default('allow_multiple_instances', False)
    if settings['allow_multiple_instances', bool]:
        # Using multiple instances, get a new application
        app = QtGui.QApplication(sys.argv)
    else:
        # Make sure we only have a single instance
        app = get_app('hyperspyui')

    log_file = _get_logfile()
    if log_file:
        sys.stdout = sys.stderr = log_file
    else:
        log_file = dummy_context_manager()

    with log_file:
        # Create and display the splash screen
        splash_pix = QtGui.QPixmap(
            os.path.dirname(__file__) + './images/splash.png')
        splash = QtGui.QSplashScreen(splash_pix,
                                     QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        app.processEvents()

        # Need to have import here, as it can take some time, so should happen
        # after displaying splash
        from hyperspyui.mainwindow import MainWindow

        form = MainWindow()
        if not settings['allow_multiple_instances', bool]:
            if QT_BINDING == 'pyqt':
                app.messageAvailable.connect(form.handleSecondInstance)
            elif QT_BINDING == 'pyside':
                app.messageReceived.connect(form.handleSecondInstance)
        form.showMaximized()

        splash.finish(form)
        form.load_complete.emit()

        app.exec_()

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    sys.path.append(os.path.dirname(__file__))
    main()
