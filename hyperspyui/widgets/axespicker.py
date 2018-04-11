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


from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtWidgets import QDialogButtonBox

from hyperspyui.widgets.extendedqwidgets import ExToolWindow


class AxesPickerDialog(ExToolWindow):
    def __init__(self, ui, signal, single=False):
        super().__init__(ui)
        self.ui = ui
        self.single = single
        self.signal = signal
        self.create_controls()
        self.setWindowTitle("Select axes")

    @property
    def selected_axes(self):
        sel = self.list.selectedItems()
        if self.single:
            if len(sel) == 0:
                return None
            elif len(sel) == 1:
                return sel[0].data(QtCore.Qt.UserRole)
            else:
                raise ValueError("Invalid selection")
        else:
            return [i.data(QtCore.Qt.UserRole) for i in sel]

    def create_controls(self):
        self.list = QtWidgets.QListWidget()
        for ax in self.signal.axes_manager._get_axes_in_natural_order():
            rep = '%s axis, size: %i' % (ax._get_name(), ax.size)
            item = QtWidgets.QListWidgetItem(rep, self.list)
            item.setData(QtCore.Qt.UserRole, ax)
            self.list.addItem(item)
        if not self.single:
            self.list.setSelectionMode(
                QtGui.QAbstractItemView.ExtendedSelection)
        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal)

        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.list)
        vbox.addWidget(btns)

        self.setLayout(vbox)
