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
Created on Sun Aug 21 19:59:04 2016

@author: Vidar Tonaas Fauske
"""


from qtpy import QtCore, QtWidgets


# QAction.trigger/activate are not virtual, so cannot simply override.
# Instead, we shadow/wrap the triggered signal used by our python code
class AdvancedAction(QtWidgets.QAction):
    # The overloaded signal can take an optional argument `advanced`
    _triggered = QtCore.Signal([], [bool], [bool, bool])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # not working on pyside, not tested on pyside2 because of pyface issue
        super().triggered[bool].connect(self._trigger)

    @property
    def triggered(self):
        return self._triggered

    def _trigger(self, checked):
        mods = QtWidgets.QApplication.keyboardModifiers()
        advanced = mods & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier
        self._triggered[bool, bool].emit(checked, advanced)
        self._triggered[bool].emit(checked)
        self._triggered.emit()

    def setIcon(self, icon):
        # We need to keep a reference to the icon object if not it will be
        # garbage collected
        # See https://www.riverbankcomputing.com/pipermail/pyqt/2019-March/041459.html
        self._icon = icon
        super().setIcon(icon)

AdvancedAction.__init__.__doc__ = QtWidgets.QAction.__init__.__doc__
