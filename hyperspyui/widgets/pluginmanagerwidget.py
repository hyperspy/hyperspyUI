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
Created on Sun Mar 01 03:24:48 2015

@author: Vidar Tonaas Fauske
"""

import sys
import os

from qtpy import QtCore
from qtpy.QtCore import Qt, QModelIndex
from qtpy.QtWidgets import (QDialogButtonBox, QTableView, QHeaderView,
                            QPushButton, QVBoxLayout)

from .extendedqwidgets import ExToolWindow
from .editorwidget import EditorWidget


def tr(text):
    return QtCore.QCoreApplication.translate("PluginManagerWidget", text)


class PluginsModel(QtCore.QAbstractItemModel):

    EnabledColumn = 0
    NameColumn = 1
    PathColumn = 2

    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self._update_data()

    def _update_data(self):
        self._plugin_data = []
        for i, (name, (enabled, ptype)) in enumerate(
                self.plugin_manager._enabled.items()):
            path = sys.modules[ptype.__module__].__file__
            path = os.path.normpath(path)
            if path.endswith('.pyc') or path.endswith('.pyo'):
                path = path[:-1]
            self._plugin_data.append([enabled, name, path])

    def flags(self, index):
        if index.column() in [self.NameColumn, self.PathColumn]:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        elif index.column() == self.EnabledColumn:
            return (Qt.ItemIsEditable | Qt.ItemIsUserCheckable |
                    Qt.ItemIsEnabled)
        return None

    def parent(self, index):
        return QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def data(self, index, role=Qt.DisplayRole):
        self._update_data()
        r, c = index.row(), index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if c == self.EnabledColumn:
                return None
            else:
                return self._plugin_data[r][c]
        elif role == Qt.CheckStateRole:
            if c == self.EnabledColumn:
                if self._plugin_data[r][c]:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
        return None

    def setData(self, index, value, role=Qt.EditRole):
        r, c = index.row(), index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if c == self.EnabledColumn:
                name = self._plugin_data[r][self.NameColumn]
                self._plugin_data[r][c] = bool(value)
                self.plugin_manager.enable_plugin(name, bool(value))
                return True
        if role == Qt.CheckStateRole:
            if c == self.EnabledColumn:
                name = self._plugin_data[r][self.NameColumn]
                enabled = (value != Qt.Unchecked)
                self._plugin_data[r][c] = enabled
                self.plugin_manager.enable_plugin(name, enabled)
                return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == self.EnabledColumn:
                    return tr("Enabled")
                elif section == self.NameColumn:
                    return tr("Name")
                elif section == self.PathColumn:
                    return tr("Path")
        return None

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._plugin_data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3


class PluginManagerWidget(ExToolWindow):

    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)

        self.setWindowTitle(tr("Plugin manager"))
        self.plugin_manager = plugin_manager
        self.create_controls()

    def edit_plugin(self):
        i = self.table.currentIndex()
        if not i.isValid():
            return None
        if i.column() != PluginsModel.PathColumn:
            i = i.sibling(i.row(), PluginsModel.PathColumn)
        path = self.model.data(i)
        if path is not None and os.path.isfile(path):
            ui = self.plugin_manager.ui
            e = EditorWidget(ui, ui, path)
            ui.editors.append(e)
            e.is_plugin = True
            e.show()

    def create_controls(self):
        table = QTableView(self)
        self.model = PluginsModel(self.plugin_manager)
        table.setModel(self.model)
        h = table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setHorizontalHeader(h)
        h = table.verticalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setVerticalHeader(h)
        self.table = table
        width = 80
        for i in range(3):
            width += table.columnWidth(i)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                Qt.Horizontal)
        self.edit_btn = QPushButton("Edit")
        btns.addButton(self.edit_btn, QDialogButtonBox.ActionRole)
        self.edit_btn.clicked.connect(self.edit_plugin)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(table)
        vbox.addWidget(btns)
        self.setLayout(vbox)
        s = self.size()
        s.setHeight(table.rowHeight(0) * 10)
        s.setWidth(width)
        self.resize(s)
