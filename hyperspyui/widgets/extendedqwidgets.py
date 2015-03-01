# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 22:11:04 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import numpy as np


def tr(text):
    return QCoreApplication.translate("ExtendedQWidgets", text)


class ExToolWindow(QDialog):

    """
    QDialog with Qt.Tool window flags.
    """

    def __init__(self, parent=None):
        super(ExToolWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Tool)


class ExClickLabel(QLabel):

    """
    QLabel with 'clicked()' signal.
    """
    clicked = Signal()

    def _init__(self, *args, **kwargs):
        super(ExClickLabel, self).__init__(*args, **kwargs)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super(ExClickLabel, self).mouseReleaseEvent(event)


class ExMessageBox(QMessageBox):

    def isChecked(self):
        cb = self.checkBox()
        if cb is None:
            raise AttributeError
        return cb.checkState() == Qt.Checked

    def setCheckBox(self, cb):
        try:
            super(ExMessageBox, self).setCheckBox(cb)
        except AttributeError:
            oldcb = self.checkBox()
            if oldcb is not None:
                self.removeButton(oldcb)
            self._checkBox = cb
            if cb is not None:
                cb.blockSignals(True)
                self.addButton(cb, QMessageBox.ResetRole)

    def checkBox(self):
        try:
            return super(ExMessageBox, self).checkBox()
        except AttributeError:
            pass
        try:
            return self._checkBox
        except AttributeError:
            return None


class ExRememberPrompt(ExMessageBox):

    def __init__(self, *args, **kwargs):
        super(ExRememberPrompt, self).__init__(*args, **kwargs)
        cb = QCheckBox(tr("Remember this choice"))
        self.setCheckBox(cb)


class ExDoubleSlider(QSlider):

    """
    QSlider with double values instead of int values.
    """
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None, orientation=None):
        if orientation is None:
            super(ExDoubleSlider, self).__init__(parent)
        else:
            super(ExDoubleSlider, self).__init__(orientation, parent)
        self.steps = 1000
        self._range = (0.0, 1.0)
        self.connect(self, SIGNAL('valueChanged(int)'), self._on_change)

    def setRange(self, vmin, vmax):
        if isinstance(vmin, (np.complex64, np.complex128)):
            vmin = np.abs(vmin)
        if isinstance(vmax, (np.complex64, np.complex128)):
            vmax = np.abs(vmax)
        self._range = (vmin, vmax)
        return super(ExDoubleSlider, self).setRange(0, self.steps)

    def setValue(self, value):
        vmin, vmax = self._range
        if isinstance(value, (np.complex64, np.complex128)):
            value = np.abs(value)
        try:
            v = int((value - vmin) * self.steps / (vmax - vmin))
        except (ZeroDivisionError, OverflowError, ValueError):
            v = 0
            self.setEnabled(False)
        return super(ExDoubleSlider, self).setValue(v)

    def value(self):
        v = super(ExDoubleSlider, self).value()
        return self._int2dbl(v)

    def _int2dbl(self, intval):
        vmin, vmax = self._range
        return vmin + intval * (vmax - vmin) / self.steps

    def _on_change(self, intval):
        dblval = self._int2dbl(intval)
        self.valueChanged.emit(dblval)
