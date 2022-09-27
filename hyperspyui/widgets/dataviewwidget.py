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
Created on Tue Nov 04 16:32:55 2014

@author: Vidar Tonaas Fauske
"""

import os

from qtpy import QtGui, QtCore, QtSvg, QtWidgets
from qtpy.QtCore import Qt

from functools import partial
import traits.api as t
import traitsui.api as tu

from hyperspyui.util import create_add_component_actions, win2sig


def tr(text):
    return QtCore.QCoreApplication.translate("DataViewWidget", text)


NameCol = 1
VisibilityCol = 0


class ComponentEditorHandler(tu.Handler):

    def setattr(self, info, object, name, value):
        # Set the value etc.
        tu.Handler.setattr(self, info, object, name, value)
        if name in ('value', 'std'):
            try:
                # Make sure the value is actually stored in array
                object.store_current_value_in_array()
            except AttributeError:
                # in case some attribute are missing
                pass


class VisbilityDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, icons=None):
        if icons is None or len(icons) < 1:
            icons = []
            path = os.path.dirname(__file__)
            for fn in [path + "/../images/visibility_on.svg",
                       path + "/../images/visibility_off.svg"]:
                renderer = QtSvg.QSvgRenderer(fn)
                pm = QtGui.QPixmap(12, 12)
                pm.fill(Qt.transparent)
                painter = QtGui.QPainter(pm)
                renderer.render(painter)
                icons.append(pm)
            icons = tuple(icons)
        elif len(icons) < 2:
            icons = tuple(icons) + (QtGui.QPixmap(),)
        else:
            icons = tuple(icons)
        self.icons = icons
        self.margin = 2
        super().__init__(parent)

    def iconPos(self, icon, option):
        return QtCore.QPoint(int(option.rect.right() - icon.width() - self.margin),
                             int(option.rect.center().y() - icon.height()/2))

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)

        # Make sure we have room for the icon
        if Qt.Checked == index.data(Qt.CheckStateRole):
            icon = self.icons[0]
        else:
            icon = self.icons[1]
        size.setWidth(max(size.width(), + icon.width() + self.margin * 2))
        size.setHeight(max(size.height(), icon.height() + self.margin * 2))
        return size

    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        if Qt.Checked == index.data(Qt.CheckStateRole):
            icon = self.icons[0]
        elif Qt.Unchecked == index.data(Qt.CheckStateRole):
            icon = self.icons[1]
        else:
            return
        painter.drawPixmap(self.iconPos(icon, option), icon)


class HyperspyItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, parent, itemtype, hspy_item):
        super().__init__(parent, itemtype)
        self.hspy_item = hspy_item
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable |
                Qt.ItemIsEnabled)
        self.setText(NameCol, hspy_item.name)

    def data(self, column, role):
        if column == NameCol:
            if role == Qt.UserRole:
                return self.hspy_item
        elif column == VisibilityCol:
            if role == Qt.CheckStateRole:
                # Asking about visibility
                # Only return valid state for SignalType
                if self.type() == DataViewWidget.SignalType:
                    s = self.hspy_item
                    vis = False
                    for w in [s.navigator_plot, s.signal_plot]:
                        if w is not None and not w.isMinimized():
                            vis = True
                    if vis:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked
                else:
                    return None
        return super().data(column, role)

    def setData(self, column, role, value):
        if column == VisibilityCol and role == Qt.CheckStateRole \
                and self.type() == DataViewWidget.SignalType:
            self._on_toggle_visibility()
        else:
            super().setData(column, role, value)

    def _on_toggle_visibility(self):
        checked = Qt.Checked == self.data(VisibilityCol, Qt.CheckStateRole)
        s = self.hspy_item
        figs = [p for p in (s.signal_plot, s.navigator_plot) if p is not None]
        if len(figs) < 1:
            return
        for p in figs:
            if checked:
                p.showMinimized()
            else:
                if p.isMinimized():
                    p.showNormal()
                else:
                    self.treeWidget().main_window.main_frame.\
                        setActiveSubWindow(p)


class DataViewWidget(QtWidgets.QWidget):

    """
    A custom QTreeWidget, that handles the Signal-Model-Component hierarchy.
    The relationships are displayed in a tree structure, and helps keep track
    of the relationships between them. Also makes handeling several Models per
    Signal easier.
    """

    # Enums
    SignalType = QtWidgets.QTreeWidgetItem.UserType
    ModelType = QtWidgets.QTreeWidgetItem.UserType + 1
    ComponentType = QtWidgets.QTreeWidgetItem.UserType + 2

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.header().close()
        self.lut = {}
        self.editor_visible = True
        self.tree.setColumnCount(2)
        self.editor = QtWidgets.QVBoxLayout()
        self.editor_bottom_padding = 20

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.addLayout(self.editor)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        sp = self.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(sp)
        sp = self.tree.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.tree.setSizePolicy(sp)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested[QtCore.QPoint].connect(self.onCustomContextMenu)
        self.tree.currentItemChanged.connect(self.currentItemChanged)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)

        self.tree.setItemDelegateForColumn(VisibilityCol,
                                           VisbilityDelegate(self.tree))
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def _add(self, item, itemtype, parent=None):
        """
        Make a QTreeWidgetItem for data item, and insert it below parent.
        The parent can be either a data item, or a QTreeWidgetItem.
        """
        if parent is None:
            parent = self.tree
        elif not isinstance(parent, QtWidgets.QTreeWidgetItem):
            parent = self.lut[parent]
        twi = HyperspyItem(parent, itemtype, item)
        if itemtype == self.SignalType:
            self.tree.resizeColumnToContents(VisibilityCol)
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
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
        traits_dialog.setSizePolicy(sp)
        self.editor.addWidget(traits_dialog)
        self.editor.addSpacing(self.editor_bottom_padding)
        traits_dialog.show()

    def currentItemChanged(self, current, previous):
        if self.editor_visible:
            if current and current.type() == self.ComponentType:
                comp = current.data(NameCol, Qt.UserRole)
                if isinstance(comp, t.HasTraits):
                    self.main_window.capture_traits_dialog(
                        self.set_traits_editor)
                    self.edit_traits(comp, False)
            else:
                self.clear_editor()

    def itemDoubleClicked(self, item, column):
        if column == VisibilityCol:
            return      # Don't count double clicks on check
        if item.type() == self.ComponentType:
            item = item.parent().parent()
        elif item.type() == self.ModelType:
            item = item.parent()
        val = Qt.Checked == item.data(VisibilityCol, Qt.CheckStateRole)
        state = Qt.Checked if not val else Qt.Unchecked
        item.setData(VisibilityCol, Qt.CheckStateRole, state)

    def edit_traits(self, comp, buttons=True):
        try:
            items = [tu.Item('name'), tu.Item('active')]
            for p in comp.parameters:
                name = '.'.join(('object', p.name))
                p_label = p.name.replace('_', ' ').capitalize()
                vi = tu.Item(name + '.value', label=p_label,
                             editor=tu.RangeEditor(low_name=name + '.bmin',
                                                   high_name=name + '.bmax'))
                items.extend((vi, tu.Item(name + '.free')))
            view = tu.View(*items,
                           handler=ComponentEditorHandler(),
                           buttons=tu.OKCancelButtons if buttons else [],
                           default_button=tu.OKButton,
                           kind='live',
                           resizable=True)
            comp.edit_traits(view=view)
        except AttributeError:
            # in case some attribute are missing
            pass

    def onCustomContextMenu(self, point):
        """
        Displays the context menu for whatever is under the supplied point.
        """
        item = self.tree.itemAt(point)
        if not item:
            return
        cm = QtWidgets.QMenu(self.tree)
        if item.type() == self.SignalType:
            sig = item.data(NameCol, Qt.UserRole)

            # Add all actions defined on object
            for ac in sig.actions.values():
                cm.addAction(ac)

        elif item.type() == self.ModelType:
            model = item.data(NameCol, Qt.UserRole)

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
            comp = item.data(NameCol, Qt.UserRole)
            model = item.parent().data(NameCol, Qt.UserRole)

            # Fit action
            ac = QtWidgets.QAction(tr("&Fit component"), self.tree)
            f = partial(model.fit_component, comp)
            ac.triggered.connect(f)
            cm.addAction(ac)

            # Configure action
            ac = QtWidgets.QAction(tr("&Configure"), self.tree)
            f = partial(self.edit_traits, comp)
            ac.triggered.connect(f)
            cm.addAction(ac)

            cm.addSeparator()

            # Remove action
            ac = QtWidgets.QAction(tr("&Delete"), self.tree)
            f = partial(model.remove_component, comp)
            ac.triggered.connect(f)
            cm.addAction(ac)
        cm.exec_(self.tree.mapToGlobal(point))

    def keyPressEvent(self, event):
        citem = self.tree.currentItem()
        if event.key() == Qt.Key_Delete:
            data = citem.data(NameCol, Qt.UserRole)
            if citem.type() == self.SignalType:
                data.close()
            elif citem.type() == self.ModelType:
                data.actions['delete'].trigger()
            elif citem.type() == self.ComponentType:
                model = citem.parent().data(NameCol, Qt.UserRole)
                model.remove_component(data)
        else:
            super().keyPressEvent(event)

    def _remove(self, key):
        if key in self.lut:
            item = self.lut[key]
            if item.parent() is None:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
            else:
                item.parent().removeChild(item)
            self.lut.pop(key)

    def add_signal(self, signal):
        item = self._add(signal, self.SignalType)
        signal.model_added[object].connect(self.add_model)
        signal.model_removed[object].connect(self.remove)

        for m in signal.models:
            self.add_model(m, signal)
        self.tree.setCurrentItem(item)

    def add_model(self, model, signal=None):
        if signal is None:
            signal = model.signal
        self._add(model, self.ModelType, parent=signal)
        model.added[object, object].connect(self.add_component)
        model.removed[object].connect(self.remove)
        for c in model.components.values():
            self.add_component(c, model)

    def add_component(self, component, model):
        ci = self._add(component, self.ComponentType,
                       parent=model)
        if isinstance(component, t.HasTraits):
            def update_name(new_name):
                ci.setText(NameCol, new_name)
            component.on_trait_change(update_name, 'name')

    def add(self, object, type, parent=None):
        self._add(object, type, parent)

    def remove(self, object):
        self._remove(object)

    def on_mdiwin_activated(self, mdi_figure):
        """
        Can be connected to an MdiArea's subWindowActivated signal to sync
        the selected signal.
        """
        sf = win2sig(mdi_figure, self.main_window.signals)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            s = item.data(NameCol, Qt.UserRole)
            # In case topLevelItems are not all SignalWrappers in future
            if s is sf and s is not self.get_selected_wrapper():
                self.tree.setCurrentItem(item)
                return

    def get_selected_wrappers(self):
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
            s = i.data(NameCol, Qt.UserRole)
            if s not in signals:
                signals.append(s)

        return signals

    def get_selected_wrapper(self):
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
        return item.data(NameCol, Qt.UserRole)

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
        return item.data(NameCol, Qt.UserRole)

    def get_selected_component(self):
        raise NotImplementedError()
