# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 03:01:19 2014

@author: Vidar Tonaas Fauske
"""


import sys
import pickle
from python_qt_binding import QtGui, QtCore, QtNetwork, QT_BINDING


class SingleApplication(QtGui.QApplication):
    messageAvailable = QtCore.pyqtSignal(object)

    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())

    def isRunning(self):
        return self._running


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
                print(socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False


def get_app(key):
    # send commandline args as message
    if QT_BINDING == 'pyqt':
        if len(sys.argv) > 1:
            app = SingleApplicationWithMessaging(sys.argv, key)
            if app.isRunning():
                msg = pickle.dumps(sys.argv)
                app.sendMessage(msg)
                sys.exit(1)
        else:
            app = SingleApplication(sys.argv, key)
            if app.isRunning():
                sys.exit(1)
    elif QT_BINDING == 'pyside':
        from siding.singleinstance import QSingleApplication
        app = QSingleApplication(sys.argv)
        msg = pickle.dumps(sys.argv[1:])
        app.ensure_single(message=msg)
    else:
        app = QtGui.QApplication(sys.argv)
    return app
