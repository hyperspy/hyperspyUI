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
Created on Thu Nov 27 03:01:19 2014

@author: Vidar Tonaas Fauske
"""


import sys
import json
import os
import logging
from qtpy import QtGui, QtCore, QtNetwork, API, QtWidgets

_logger = logging.getLogger(__name__)


class SingleApplication(QtWidgets.QApplication):
    messageAvailable = QtCore.Signal(object)

    def __init__(self, argv, key):
        QtWidgets.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())

        # Set correct logo
        base_path = os.path.abspath(os.path.dirname(__file__))
        icon_path = os.path.join(base_path, 'images', 'hyperspy.svg')
        QtWidgets.QApplication.setWindowIcon(QtGui.QIcon(icon_path))
        self.aboutToQuit.connect(self.detach_shared_memory)

    def isRunning(self):
        return self._running

    def detach_shared_memory(self):
        _logger.debug('Detaching shared memory.')
        if not self._memory.detach():
            _logger.debug('Shared memory could not be detached properly.')


class SingleApplicationWithMessaging(SingleApplication):

    def __init__(self, argv, key):
        SingleApplication.__init__(self, argv, key)
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageAvailable.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                _logger.error(socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                _logger.error(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False


def get_app(key):
    # send commandline args as message
    if "pyqt" in API:
        if len(sys.argv) > 1:
            app = SingleApplicationWithMessaging(sys.argv, key)
            if app.isRunning():
                msg = json.dumps(sys.argv[1:])
                app.sendMessage(msg)
                _logger.debug('An existing instance of HyperSpyUI is running, '
                              'sending arguments to it.')
                sys.exit(1)     # An instance is already running
        else:
            app = SingleApplicationWithMessaging(sys.argv, key)
            if app.isRunning():
                _logger.debug('An existing instance of HyperSpyUI is running, '
                              'bringing it to the front.')
                sys.exit(1)     # An instance is already running
    elif API == 'pyside':
        from siding.singleinstance import QSingleApplication
        app = QSingleApplication(sys.argv)
        msg = json.dumps(sys.argv[1:])
        app.ensure_single(message=msg)
    else:
        app = QtWidgets.QApplication(sys.argv)
    return app
