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

from functools import partial
from collections import OrderedDict

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QDialogButtonBox
from qtpy.QtCore import Qt, QModelIndex

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.widgets.extendedqwidgets import ExToolWindow
from hyperspy.misc.utils import DictionaryTreeBrowser


def tr(text):
    return QtCore.QCoreApplication.translate("MetadataEditor", text)


class MetadataEditor(Plugin):
    name = "Metadata Editor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editors = {}

    def create_actions(self):
        self.add_action(self.name + '.view_metadata',
                        tr("View metadata"),
                        self.edit_metadata,
                        tip=tr("View/edit signal meatadata"))

    def create_menu(self):
        self.add_menuitem(
            'Signal', self.ui.actions[self.name + '.view_metadata'])

    def _on_close(self, signal):
        self.editors.pop(signal)

    def edit_metadata(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        if signal in self.editors:
            self.editors[signal].show()
        else:
            diag = ExToolWindow(parent=self.ui)
            sw = self.ui.lut_signalwrapper[signal]
            diag.setWindowTitle(tr("Metadata of %s") % sw.name)
            vbox = QtWidgets.QVBoxLayout()
            tw = MetadataTreeWidget(signal)
            vbox.addWidget(tw)
            btns = QDialogButtonBox(QDialogButtonBox.Ok)
            btns.accepted.connect(diag.accept)
            vbox.addWidget(btns)
            diag.setLayout(vbox)
            diag.show()
            diag.finished.connect(partial(self._on_close, signal))
            self.editors[signal] = diag


class MetadataTreeWidget(QtWidgets.QTreeView):

    def __init__(self, signal, parent=None):
        super().__init__(parent)
        self.signal = signal
        self._model = MetadataModel(signal)
        self.setModel(self._model)
        self.setAlternatingRowColors(True)
        self.setColumnWidth(0, 300)
        self.setColumnWidth(0, 300)
#        self.setEditTriggers(
#            QAbstractItemView.DoubleClicked |
#            QAbstractItemView.SelectedClicked |
#            QAbstractItemView.EditKeyPressed)
        # Expand 'metadata' by default
        self.expand(self._model.index(0, 0))

    def sizeHint(self):
        hint = super().sizeHint()
        hint.setWidth(600)
        return hint


# Parts of the following code has the following licence:
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the
# "LICENSE" file, which should be included with this package. The terms are
# also available at http://www.gnu.org/licenses/gpl-3.0.html

class MetadataNode:
    def __init__(self, model, parent, name, ref, row):
        self._subnodes = None
        self.ref = ref
        self.model = model
        self.parent = parent
        self.row = row
        self.name = name

    def _getChildren(self):
        if isinstance(self.ref, DictionaryTreeBrowser):
            return OrderedDict(self.ref)
        else:
            return {}

    def _createNode(self, name, ref, row):
        return MetadataNode(self.model, self, name, ref, row)

    @property
    def subnodes(self):
        if self._subnodes is None:
            children = self._getChildren()
            self._subnodes = []
            for index, (name, child) in enumerate(children.items()):
                node = self._createNode(name, child, index)
                self._subnodes.append(node)
        return self._subnodes

    @property
    def index(self):
        return self.model.createIndex(self.row, 0, self)

    def edit_value(self, value):
        if self.parent and isinstance(self.ref, (int, str, bool, float)):
            # Immutable type, make sure we change value in parent!
            self.parent.ref[self.name] = value
            self.ref = value
            return True
        return False


class MetadataModel(QtCore.QAbstractItemModel):

    def __init__(self, signal, parent=None):
        super().__init__(parent=parent)
        self.nodes = [
            MetadataNode(self, None, 'metadata', signal.metadata, 0),
            MetadataNode(self, None, 'original_metadata',
                         signal.original_metadata, 1)]

    def index(self, row, column, parent=None):
        if parent and parent.isValid():
            node = parent.internalPointer()
            ref = node.subnodes[row]
        else:
            ref = self.nodes[row]
        return self.createIndex(row, column, ref)

    def parent(self, index):
        if index is None or not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, node.parent)

    def rowCount(self, parent=None):
        if parent is None or not parent.isValid():
            return len(self.nodes)
        else:
            return len(parent.internalPointer().subnodes)

    def columnCount(self, parent=None):
        return 2

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index and index.isValid() and index.column() == 1:
            node = index.internalPointer()
            if not isinstance(node.ref, DictionaryTreeBrowser):
                if isinstance(node.ref, bool):
                    flags |= Qt.ItemIsUserCheckable
                elif isinstance(node.ref, (str, int, float)):
                    flags |= Qt.ItemIsEditable
        return flags

    def data(self, index, role):
        if index is None or not index.isValid():
            return None
        node = index.internalPointer()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() == 0:
                return node.name
            if (index.column() == 1 and
                    not isinstance(node.ref, DictionaryTreeBrowser)):
                return str(node.ref)
        elif role == Qt.CheckStateRole:
            if index.column() == 1 and isinstance(node.ref, bool):
                return Qt.Checked if node.ref else Qt.Unchecked
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignTop
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index is None or not index.isValid() or index.column() != 1:
            return False
        node = index.internalPointer()
        value_changed = False
        input_ok = False
        if role == Qt.CheckStateRole:
            if isinstance(node.ref, bool):
                value = value == Qt.Checked
                input_ok = True
                if node.ref != value:
                    node.edit_value(value)
                    value_changed = True
        elif role == Qt.EditRole:
            if isinstance(node.ref, (str, int, float)):
                try:
                    value = type(node.ref)(value)
                except ValueError:
                    pass
                else:
                    input_ok = True
                    if node.ref != value:
                        node.edit_value(value)
                        value_changed = True
        else:
            return super().setData(index, value, role)
        if value_changed:
            self.dataChanged.emit(index, index)
        return input_ok

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return 'Key'
            elif column == 1:
                return 'Value'
        return None

    def reset(self):
        super().beginResetModel()
        self.invalidate()
        self._ref2node = {}
        self._dummyNodes = set()
        super().endResetModel()
