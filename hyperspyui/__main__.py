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

from packaging.version import Version
import os
import platform
import sys
import locale
from contextlib import contextmanager


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
# TODO: Variable explorer (Signal/Model etc.). 3rd party library?
# TODO: Disable tools when no figure


import logging
logging.basicConfig()
# Note that this might be overriden during hyperspy import
LOGLEVEL = logging.INFO
logging.getLogger('hyperspy').setLevel(LOGLEVEL)
logging.getLogger('hyperspyui').setLevel(LOGLEVEL)


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


def get_splash():
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QApplication, QSplashScreen
    from qtpy.QtGui import QColor, QPixmap
    splash_pix = QPixmap(os.path.join(
        os.path.dirname(__file__), 'images', 'splash.png'))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage("Initializing...", Qt.AlignBottom | Qt.AlignCenter |
                       Qt.AlignAbsolute, QColor(Qt.white))
    QApplication.processEvents()
    return splash


def main():
    from qtpy.QtCore import Qt, QCoreApplication, qVersion
    from qtpy.QtWidgets import QApplication
    from qtpy import API

    # Fixes issues with Big Sur
    # https://bugreports.qt.io/browse/QTBUG-87014, fixed in qt 5.15.2
    if (sys.platform == 'darwin' and
            Version(platform.mac_ver()[0]) >= Version("10.16") and
            Version(qVersion()) < Version("5.15.2") and
            "QT_MAC_WANTS_LAYER" not in os.environ):
        os.environ["QT_MAC_WANTS_LAYER"] = "1"

    from hyperspyui.version import __version__
    from hyperspyui.settings import Settings

    # QtWebEngineWidgets must be imported before a QCoreApplication instance
    # is created (used in eelsdb plugin)
    # Avoid a bug in Qt: https://bugreports.qt.io/browse/QTBUG-46720
    from qtpy import QtWebEngineWidgets

    # Need to set early to make QSettings accessible
    QCoreApplication.setApplicationName("HyperSpyUI")
    QCoreApplication.setOrganizationName("Hyperspy")
    QCoreApplication.setApplicationVersion(__version__)
    # To avoid the warning:
    # Qt WebEngine seems to be initialized from a plugin. Please set
    # Qt::AA_ShareOpenGLContexts using QCoreApplication::setAttribute before
    # constructing QGuiApplication.
    # Only available for pyqt>=5.4
    if hasattr(Qt, "AA_ShareOpenGLContexts"):
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    # First, clear all default settings!
    # TODO: This will cause a concurrency issue with multiple launch
    Settings.clear_defaults()
    # Setup default for single/multi-instance
    settings = Settings(group="General")
    settings.set_default('allow_multiple_instances', False)
    if settings['allow_multiple_instances', bool]:
        # Using multiple instances, get a new application
        app = QApplication(sys.argv)
    else:
        # Make sure we only have a single instance
        from hyperspyui.singleapplication import get_app
        app = get_app('hyperspyui')

    splash = get_splash()

    log_file = _get_logfile()
    if log_file:
        sys.stdout = sys.stderr = log_file
    else:
        @contextmanager
        def dummy_context_manager(*args, **kwargs):
            yield
        log_file = dummy_context_manager()

    with log_file:
        # Need to have import here, since QApplication needs to be called first
        from hyperspyui.mainwindow import MainWindow

        form = MainWindow(splash=splash)
        if not settings['allow_multiple_instances', bool]:
            if "pyqt" in API:
                app.messageAvailable.connect(form.handleSecondInstance)
            elif API == 'pyside':
                app.messageReceived.connect(form.handleSecondInstance)
        form.showMaximized()

        form.splash.hide()
        form.load_complete.emit()
        # Ensure logging is OK
        import hyperspy.api as hs
        hs.set_log_level(LOGLEVEL)

        app.exec_()


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    sys.path.append(os.path.dirname(__file__))
    main()
