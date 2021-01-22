
import os
import tempfile
import shutil

from hyperspyui.version import __version__
from hyperspyui.__main__ import get_splash

import pytest

from qtpy import QtCore

# QtWebEngineWidgets must be imported before a QCoreApplication instance
# is created (used in eelsdb plugin)
# Avoid a bug in Qt: https://bugreports.qt.io/browse/QTBUG-46720
from qtpy import QtWebEngineWidgets

QCoreApplication = QtCore.QCoreApplication
QSettings = QtCore.QSettings

QCoreApplication.setApplicationName("HyperSpyUI-tests")
QCoreApplication.setOrganizationName("Hyperspy")
QCoreApplication.setApplicationVersion(__version__)

QSettings.setDefaultFormat(QSettings.IniFormat)


_tmpdirpath = ''


def pytest_configure(config):
    global _tmpdirpath
    _tmpdirpath = tempfile.mkdtemp()
    userpath = os.path.join(_tmpdirpath, 'user')
    syspath = os.path.join(_tmpdirpath, 'sys')
    os.mkdir(userpath)
    os.mkdir(syspath)

    QSettings.setPath(QSettings.IniFormat,
                      QSettings.UserScope, userpath)
    QSettings.setPath(QSettings.IniFormat,
                      QSettings.SystemScope, syspath)

    settings = QSettings()
    settings.setValue(
        'plugins/Version selector/check_for_updates_on_start', False)


def pytest_unconfigure(config):
    shutil.rmtree(_tmpdirpath)


@pytest.fixture(scope='session')
def mainwindow(qapp):
    from hyperspyui.mainwindow import MainWindow

    window = MainWindow(get_splash(), argv=[])
    yield window
    qapp.processEvents()
    window.close()
    window.deleteLater()
    del window
    qapp.processEvents()
