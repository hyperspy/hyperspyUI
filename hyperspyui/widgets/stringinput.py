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
Created on Wed Jan 20 02:43:41 2016

@author: Vidar Tonaas Fauske
"""

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QDialogButtonBox


class StringInputDialog(QtWidgets.QDialog):

    def __init__(self, prompt="", default="", parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Input prompt")
        self.setWindowFlags(QtCore.Qt.Tool)

        frm = QtWidgets.QFormLayout()
        self.edit = QtWidgets.QLineEdit(default)
        frm.addRow(prompt, self.edit)

        btns = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                QtCore.Qt.Horizontal, self)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        box = QtWidgets.QVBoxLayout(self)
        box.addLayout(frm)
        box.addWidget(btns)
        self.setLayout(box)

    def prompt_modal(self, rejection=None):
        dr = self.exec_()
        if dr == QtWidgets.QDialog.Accepted:
            return self.edit.text()
        else:
            return rejection

    def _on_completed(self, result):
        (callback, rejection) = self._on_completed_info
        if result == QtWidgets.QDialog.Accepted:
            value = self.edit.text()
        else:
            value = rejection
        callback(value)

    def prompt_modeless(self, callback, rejection=None):
        self._on_completed_info = (callback, rejection)
        dr = self.show()
        dr.finished.connect(self._on_completed)
