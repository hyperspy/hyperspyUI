# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:32:55 2014

@author: vidarton
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from functools import partial

from util import create_add_component_actions

class DataViewWidget(QTreeWidget):
    SignalType = QTreeWidgetItem.UserType
    ModelType = QTreeWidgetItem.UserType + 1
    ComponentType = QTreeWidgetItem.UserType + 2
    
    def __init__(self, parent=None):
        super(DataViewWidget, self).__init__(parent)
        self.header().close()
        self.lut = {}
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.editor = QWidget()
        sp = self.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.setSizePolicy(sp)
#        self.setColumnCount(1)
#        self.setRootIsDecorated(True)
#        self.setIndentation(20)
#        self.setItemsExpandable(True)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu);
        self.connect(self, SIGNAL('customContextMenuRequested(QPoint)'), 
                     self.onCustomContextMenu)

    def _add(self, text, item, itemtype, parent=None):
        if parent is None:
            parent = self
        elif not isinstance(parent, QTreeWidgetItem):
            parent = self.lut[parent]
        twi = QTreeWidgetItem(parent, itemtype)
        twi.setText(0, text)
        twi.setData(0, Qt.UserRole, item)
        twi.setExpanded(True)
        self.lut[item] = twi
        if parent is self:
            self.addTopLevelItem(twi)
        else:
            parent.addChild(twi)
        return twi
        
    def onCustomContextMenu(self, point):
        item = self.itemAt(point)
        cm = QMenu(self)
        if item.type() == self.SignalType:
            sig = item.data(0, Qt.UserRole)
            
            cm.addAction(sig.actions['plot'])
            cm.addAction(sig.actions['add_model'])
            cm.addSeparator()
            cm.addAction(sig.actions['close'])
            
        elif item.type() == self.ModelType:
            model = item.data(0, Qt.UserRole)
            
            for ac in model.actions.values():
                cm.addAction(ac)
            
            cm.addSeparator()
            
            # Add component
            comp_actions = create_add_component_actions(self, 
                                                        model.add_component,
                                                        prefix="Add ")
            for ac in comp_actions.values():
                cm.addAction(ac)
        elif item.type() == self.ComponentType:
            comp = item.data(0, Qt.UserRole)
            model = item.parent().data(0, Qt.UserRole)
            
            # Fit action
            ac = QAction("&Fit component", self)    # TODO: tr()
            f = partial(model.fit_component, comp)
            self.connect(ac, SIGNAL('triggered()'), f)
            cm.addAction(ac)
            
            cm.addSeparator()
            
            # Remove action
            ac = QAction("&Delete", self)   # TODO: tr()
            f = partial(model.remove_component, comp)
            self.connect(ac, SIGNAL('triggered()'), f)
            cm.addAction(ac)
        cm.exec_(self.mapToGlobal(point))
    
    def _remove(self, key):
        if self.lut.has_key(key):
            item = self.lut[key]
            if item.parent() is None:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            else:
                item.parent().removeChild(item)
            self.lut.pop(key)
        
    def add_signal(self, signal):
        self._add(signal.name, signal, self.SignalType)
        signal.model_added[object].connect(self.add_model)
        signal.model_removed[object].connect(self.remove)
        
        for m in signal.models:
            self.add_model(m, signal)
          
    def add_model(self, model, signal=None):
        if signal is None:
            signal = model.signal
        self._add(model.name, model, self.ModelType, parent=signal)
        model.added[object, object].connect(self.add_component)
        model.removed[object].connect(self.remove)
        for c in model.components.values():
            self.add_component(c, model)
        
    def add_component(self, component, model):
        self._add(component.name, component, self.ComponentType, parent=model)
        
    def add(self, object, type, parent=None):
        self._add(object.name, object, type, parent)
        
    def remove(self, object):
        self._remove(object)
        
    def on_mdiwin_activated(self, mdi_figure):
        found = None
        for i in xrange(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            s = item.data(0, Qt.UserRole)
            try:    # In case topLevelItems are not all SignalWrappers in future
                if mdi_figure in (s.navigator_plot, s.signal_plot):
                    found = item
                    break
            except AttributeError:
                pass
        if found is not None:
            self.setCurrentItem(found)
        
    def get_selected_signals(self):
        items = self.selectedItems()
        signals = []
        for i in items:    
            if i.type() == self.ComponentType:
                i = i.parent().parent()
            elif i.type() == self.ModelType:
                i = i.parent()
            if i.type() != self.SignalType:
                raise TypeError("Selection of wrong type")
            s = i.data(0, Qt.UserRole)
            if s not in signals:
                signals.append(s)
                
        return signals
        
        
    def get_selected_signal(self):
        items = self.selectedItems()
        if len(items) < 1:
            return None
        item = items[0]
        if item.type() == self.ComponentType:
            item = item.parent().parent()
        elif item.type() == self.ModelType:
            item = item.parent()
        if item.type() != self.SignalType:
            raise TypeError("Selection of wrong type")
        return item.data(0, Qt.UserRole)
        
    def get_selected_model(self):
        items = self.selectedItems()
        if len(items) < 1:
            return None
        item = items[0]
        if item.type() == self.ComponentType:
            item = item.parent()
        elif item.type() == self.SignalType:
            if item.childCount() < 1:
                return None
            item = item.child(0)
        if item.type() != self.ModelType:
            raise TypeError("Selection of wrong type")
        return item.data(0, Qt.UserRole)
        
    def get_selected_component(self):
        raise NotImplementedError()
        
        # TODO: Make TraitsUI widget, and display one underneath the TreeView