# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 23:09:55 2014

@author: Vidar Tonaas Fauske
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.bindinglist import BindingList


class SignalList(QListWidget):

    def __init__(self, items=None, parent=None, multiselect=True):
        super(SignalList, self).__init__(parent)
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
            self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QAbstractItemView.SingleSelection)

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
        item = QListWidgetItem(object.name, self)
        item.setData(Qt.UserRole, object)
        super(SignalList, self).addItem(item)

    def addItems(self, items):
        for i in items:
            self.addItem(i)

    def insertItem(self, index, object):
        item = QListWidgetItem(object.name, self)
        item.setData(Qt.UserRole, object)
        super(SignalList, self).insertItem(index, item)

    def signal(self, index):
        if isinstance(index, int):
            return self.item(index).data(Qt.UserRole)
        elif isinstance(index, QListWidgetItem):
            return index.data(Qt.UserRole)

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
        if isinstance(key, QListWidgetItem):
            return key.data(Qt.UserRole)
