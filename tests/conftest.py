
import sys
import os
import tempfile
import shutil

import hyperspyui

import pytest

from qtpy import QtCore

QCoreApplication = QtCore.QCoreApplication
QSettings = QtCore.QSettings

QCoreApplication.setApplicationName("HyperSpyUI-tests")
QCoreApplication.setOrganizationName("Hyperspy")
QCoreApplication.setApplicationVersion(hyperspyui.info.version)

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

    window = MainWindow(argv=[])
    yield window
    qapp.processEvents()
    window.close()
    window.deleteLater()
    del window
    qapp.processEvents()
