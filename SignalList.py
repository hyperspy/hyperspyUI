# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 23:09:55 2014

@author: vidarton
"""


from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from BindingList import BindingList
#from SignalUIWrapper import SignalUIWrapper

class SignalList(QListWidget):
    def __init__(self, items=None, parent=None):
        super(SignalList, self).__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if items is not None:
            self.addItems(items)
            if isinstance(items, BindingList):
                self.bind(items)
            
    def bind(self, blist):
        blist.add_target(self)
        
    def addItem(self, object):
        item = QListWidgetItem(object.name, self)
        item.setData(Qt.UserRole, object)
        super(SignalList, self).addItem(item)
            
    def addItems(self, items):
        it = []
        for i in items:
            item = QListWidgetItem(object.name, self)
            item.setData(Qt.UserRole, object)
            it.append(item)
        super(SignalList, self).addItems(it)
            
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
        return sigs
        
    def __getitem__(self, key):
        if isinstance(key, QListWidgetItem):
            return key.data(Qt.UserRole)
            
#    def removeItemWidget(object):
#        super(SignalList, self).removeItemWidget(object)
#        if isinstance(object, (QListWidgetItem, QString, str)):
#            super(SingalList, self).insertItem(index, object)
#        elif isinstance(object, SignalUIWrapper):
#            super(SingalList, self).insertItem(index, object.name)
#        else:
#            super(SingalList, self).insertItem(index, str(object))
        