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
Created on Mon Oct 27 23:09:55 2014

@author: Vidar Tonaas Fauske
"""


from qtpy import QtWidgets
from qtpy.QtCore import Qt

from hyperspyui.bindinglist import BindingList


class SignalList(QtWidgets.QListWidget):

    def __init__(self, items=None, parent=None, multiselect=True):
        super().__init__(parent)
        self.multiselect = multiselect
        self._bound_blists = []

        if items is not None:
            self.addItems(items)
            if isinstance(items, BindingList):
                self.bind(items)
        self.destroyed.connect(self._on_destroy)

    @property
    def multiselect(self):
        return self._multiselect

    @multiselect.setter
    def multiselect(self, value):
        self._multiselect = value
        if value:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def bind(self, blist):
        blist.add_target(self)
        self._bound_blists.append(blist)

    def unbind(self, blist):
        blist.remove_target(self)
        self._bound_blists.remove(blist)

    def _on_destroy(self):
        for b in reversed(self._bound_blists):
            self.unbind(b)

    def addItem(self, object):
        item = QtWidgets.QListWidgetItem(object.name, self)
        item.setData(Qt.UserRole, object)
        super().addItem(item)

    def addItems(self, items):
        for i in items:
            self.addItem(i)

    def insertItem(self, index, object):
        item = QtWidgets.QListWidgetItem(object.name, self)
        item.setData(Qt.UserRole, object)
        super().insertItem(index, item)

    def signal(self, index):
        if isinstance(index, int):
            value = self.item(index).data(Qt.UserRole)
        elif isinstance(index, QtWidgets.QListWidgetItem):
            value = index.data(Qt.UserRole)
        else:
            value = None
        return value

    def get_selected(self):
        selections = self.selectedItems()
        sigs = [self.signal(i) for i in selections]
        if self.multiselect:
            return sigs
        else:
            if len(sigs) > 0:
                return sigs[0]
            else:
                return None

    def __getitem__(self, key):
        if isinstance(key, QtWidgets.QListWidgetItem):
            return key.data(Qt.UserRole)
        return None
