# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 16:32:55 2014

@author: Vidar Tonaas Fauske
"""

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from functools import partial
import traits.api as t
import traitsui.api as tu

from util import create_add_component_actions

class DataViewWidget(QWidget):
    """
    A custom QTreeWidget, that handles the Signal-Model-Component hierarchy.
    The relationships are displayed in a tree structure, and helps keep track
    of the relationships between them. Also makes handeling several Models per
    Signal easier.
    """
    
    # Enums
    SignalType = QTreeWidgetItem.UserType
    ModelType = QTreeWidgetItem.UserType + 1
    ComponentType = QTreeWidgetItem.UserType + 2
    
    def __init__(self, main_window, parent=None):
        super(DataViewWidget, self).__init__(parent)
        self.main_window = main_window
        self.tree = QTreeWidget(self)
        self.tree.header().close()
        self.lut = {}
        self.editor_visible = True
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.editor = QVBoxLayout()
        self.editor_bottom_padding = 20
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.addLayout(self.editor)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        sp = self.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.setSizePolicy(sp)
        sp = self.tree.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.tree.setSizePolicy(sp)
        
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu);
        self.connect(self.tree, SIGNAL('customContextMenuRequested(QPoint)'), 
                     self.onCustomContextMenu)
        self.tree.currentItemChanged.connect(self.currentItemChanged)

    def _add(self, text, item, itemtype, parent=None):
        """
        Make a QTreeWidgetItem for data item, and insert it below parent.
        The parent can be either a data item, or a QTreeWidgetItem.
        """
        if parent is None:
            parent = self.tree
        elif not isinstance(parent, QTreeWidgetItem):
            parent = self.lut[parent]
        twi = QTreeWidgetItem(parent, itemtype)
        twi.setText(0, text)
        twi.setData(0, Qt.UserRole, item)
        twi.setExpanded(True)
        self.lut[item] = twi
        if parent is self.tree:
            self.tree.addTopLevelItem(twi)
        else:
            parent.addChild(twi)
        return twi
        
    def clear_editor(self):
        item = self.editor.takeAt(0)
        while item:
            w = item.widget()
            if w:
                w.close()
            item = self.editor.takeAt(0)
        
    def set_traits_editor(self, traits_dialog):
        self.clear_editor()
        sp = traits_dialog.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        traits_dialog.setSizePolicy(sp)
        self.editor.addWidget(traits_dialog)
        self.editor.addSpacing(self.editor_bottom_padding)
        traits_dialog.show()
        
    def currentItemChanged(self, current, previous):
        if self.editor_visible:
            if current and current.type() == self.ComponentType:
                comp = current.data(0, Qt.UserRole)
                if isinstance(comp, t.HasTraits):
                    self.main_window.capture_traits_dialog(self.set_traits_editor)
                    self.configure_traits(comp, False)
            else:
                self.clear_editor()
                
    def configure_traits(self, comp, buttons=True):
        try:
            items = [tu.Item('name'), tu.Item('active')]
            for p in comp.parameters:
                name = '.'.join(('object', p.name))
                p_label = p.name.replace('_', ' ').capitalize()
                vi = tu.Item(name + '.value', label=p_label, 
                             editor=tu.RangeEditor(low_name=name+'.bmin',
                                                high_name=name+'.bmax'))
                items.extend((vi, tu.Item(name + '.free')))
            view = tu.View(*items, 
                        buttons=tu.OKCancelButtons if buttons else [],
                        default_button=tu.OKButton,
                        kind='live',
                        resizable=True)
            comp.edit_traits(view=view)
        except AttributeError:
            pass
        
    def onCustomContextMenu(self, point):
        """
        Displays the context menu for whatever is under the supplied point.
        """
        item = self.tree.itemAt(point)
        if not item:
            return
        cm = QMenu(self.tree)
        if item.type() == self.SignalType:
            sig = item.data(0, Qt.UserRole)
            
            # Add all actions defined on object
            for ac in sig.actions.values():
                cm.addAction(ac)
            
        elif item.type() == self.ModelType:
            model = item.data(0, Qt.UserRole)
            
            # Add all actions defined on object
            for ac in model.actions.values():
                cm.addAction(ac)
            
            # Add "add component" actions
            cm.addSeparator()
            comp_actions = create_add_component_actions(self.tree, 
                                                        model.add_component,
                                                        prefix="Add ")
            for ac in comp_actions.values():
                cm.addAction(ac)
        elif item.type() == self.ComponentType:
            comp = item.data(0, Qt.UserRole)
            model = item.parent().data(0, Qt.UserRole)
            
            # Fit action
            ac = QAction("&Fit component", self.tree)    # TODO: tr()
            f = partial(model.fit_component, comp)
            self.connect(ac, SIGNAL('triggered()'), f)
            cm.addAction(ac)
            
            # Configure action
            ac = QAction("&Configure", self.tree)
            f = partial(self.configure_traits, comp)
            ac.triggered.connect(f)
            cm.addAction(ac)
            
            cm.addSeparator()
            
            # Remove action
            ac = QAction("&Delete", self.tree)   # TODO: tr()
            f = partial(model.remove_component, comp)
            self.connect(ac, SIGNAL('triggered()'), f)
            cm.addAction(ac)
        cm.exec_(self.tree.mapToGlobal(point))
        
    def keyPressEvent(self, event):
        citem = self.tree.currentItem()
        if event.key() == Qt.Key_Delete:
            data = citem.data(0, Qt.UserRole)
            # Do nothing if SignalType
            if citem.type() == self.ModelType:
                data.actions['delete'].trigger()
            elif citem.type() == self.ComponentType:
                model = citem.parent().data(0, Qt.UserRole)
                model.remove_component(data)
        else:
            super(DataViewWidget, self).keyPressEvent(event)
    
    def _remove(self, key):
        if self.lut.has_key(key):
            item = self.lut[key]
            if item.parent() is None:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
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
        ci = self._add(component.name, component, self.ComponentType, 
                       parent=model)
        if isinstance(component, t.HasTraits):
            def update_name(new_name):
                ci.setText(0, new_name)
            component.on_trait_change(update_name, 'name')
        
    def add(self, object, type, parent=None):
        self._add(object.name, object, type, parent)
        
    def remove(self, object):
        self._remove(object)
        
    def on_mdiwin_activated(self, mdi_figure):
        """
        Can be connected to an MdiArea's subWindowActivated signal to sync
        the selected signal.
        """
        found = None
        for i in xrange(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            s = item.data(0, Qt.UserRole)
            try:    # In case topLevelItems are not all SignalWrappers in future
                if mdi_figure in (s.navigator_plot, s.signal_plot):
                    found = item
                    break
            except AttributeError:
                pass
        if found is not None and found is not self.get_selected_signal():
            self.tree.setCurrentItem(found)
        
    def get_selected_signals(self):
        """
        Returns a list of all selected signals. Any selected Models or 
        Components will select their Signal parent.
        """
        items = self.tree.selectedItems()
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
        """
        Returns the first selected Signal. Any selected Models or Components 
        will select their Signal parent.
        """
        items = self.tree.selectedItems()
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
        """
        Returns the first selected Model. Any selected Signals/Components 
        will select their Model child/parent.
        """
        items = self.tree.selectedItems()
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