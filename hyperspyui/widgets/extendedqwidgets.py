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
Created on Fri Nov 21 22:11:04 2014

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore, QtWidgets

import numpy as np


def tr(text):
    return QtCore.QCoreApplication.translate("ExtendedQWidgets", text)


class ExToolWindow(QtWidgets.QDialog):

    """
    QDialog with Qt.Tool window flags.
    """

    def __init__(self, parent=None):
        super(ExToolWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)


class FigureWidget(QtWidgets.QDockWidget):

    def __init__(self, main_window, parent=None):
        super(FigureWidget, self).__init__(parent)
        self.ui = main_window
        self._last_window = None

        self.connect_()
        self.visibilityChanged.connect(self.on_visibility)

    def connect_(self, action=None):
        """
        Connects the widget to its update trigger, which is either a supplied
        action, or by default, the subWindowActivated of the MainWindow.
        """
        if action is None:
            action = self.ui.main_frame.subWindowActivated
        action.connect(self._on_figure_change)

    def disconnect(self, action=None):
        """
        Disconnects an update trigger connected with connect().
        """
        if action is None:
            action = self.ui.main_frame.subWindowActivated
        action.disconnect(self.on_change)

    def _on_figure_change(self, window):
        """
        Called when a connected update triggers. If the window is valid, it
        sets up the traitsui dialog capture, and calls cb_make_dialog.  If the
        window is invalid, it clears the widget.
        """
        self._last_window = window

    def on_visibility(self, visible):
        if visible:
            self._on_figure_change(self._last_window)


class ExClickLabel(QtWidgets.QLabel):

    """
    QLabel with 'clicked()' signal.
    """
    clicked = QtCore.Signal()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        super(ExClickLabel, self).mouseReleaseEvent(event)


class ExMessageBox(QtWidgets.QMessageBox):

    def isChecked(self):
        cb = self.checkBox()
        if cb is None:
            raise AttributeError
        return cb.checkState() == QtCore.Qt.Checked

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
                self.addButton(cb, QtWidgets.QMessageBox.ResetRole)

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
        cb = QtWidgets.QCheckBox(tr("Remember this choice"))
        self.setCheckBox(cb)


class ExDoubleSlider(QtWidgets.QSlider):

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
        self.connect(self, QtCore.SIGNAL('valueChanged(int)'), self._on_change)

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
