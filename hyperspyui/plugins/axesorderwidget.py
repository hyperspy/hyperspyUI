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
Created on Tue Apr 28 11:00:55 2015

@author: Vidar Tonaas Fauske
"""
import collections

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import (QLabel, QPushButton, QToolButton, QVBoxLayout,
                            QHBoxLayout, QWidget)

from hyperspy.axes import DataAxis
import hyperspy.api as hs

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.util import win2sig
from hyperspyui.widgets.extendedqwidgets import FigureWidget


def tr(text):
    return QtCore.QCoreApplication.translate("AxesOrderPlugin", text)


class AxesOrderPlugin(Plugin):
    name = "Axes order widget"

    def create_widgets(self):
        w = AxesOrderWidget(self.ui, self.ui)
        w.plugin = self
        self.add_widget(w)
        w.hide()  # Initial state hidden

    def flip_axes(self, axes, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
        self.record_code("<p>.flip_axes(axes=%s)" % axes)
        if not isinstance(axes, collections.abc.Iterable):
            axes = (axes,)
        replot = False
        for axis in axes:
            if not isinstance(axis, DataAxis):
                axis = signal.axes_manager[axis]
            ax = axis.index_in_array
            slices = (slice(None),) * ax + (slice(None, None, -1), Ellipsis)
            signal.data = signal.data[slices]
            replot |= axis.navigate
        if replot:
            signal.plot()
        else:
            signal.update_plot()

    def rollaxis(self, axis, pos, signal=None):
        # Get signal
        if signal is None:
            signal = self.ui.get_selected_wrapper()
        elif isinstance(signal, hs.signals.BaseSignal):
            signal = self.ui.lut_signalwrapper[signal]
        am = signal.signal.axes_manager
        # Get DataAxis
        if not isinstance(axis, DataAxis):
            axis = am[axis]
        # Reorder
        old_idx = am._axes.index(axis) + 3j
        new_s = signal.signal.rollaxis(old_idx, pos)
        signal.switch_signal(new_s)
        self.record_code("<p>.rollaxis(%s, %s)" % (str(old_idx), str(pos)))
        signal.replot()


class AxesOrderWidget(FigureWidget):

    def __init__(self, ui, parent=None):
        super().__init__(ui, parent)
        self.setWindowTitle(tr("Axes order"))
        self.signal = None
        self.create_controls()
        self._resize_controls()

    def _on_figure_change(self, win):
        super()._on_figure_change(win)
        self.signal = win2sig(win)
        self._update_controls_from_signal(self.signal)

    def _update_controls_from_signal(self, signal):
        if signal is None:
            self.setEnabled(False)
            return
        self.setEnabled(True)
        self.lst_nav.setUpdatesEnabled(False)
        self.lst_sig.setUpdatesEnabled(False)
        self._updating = True

        self.lst_nav.clear()
        self.lst_sig.clear()

        for ax in signal.signal.axes_manager._get_axes_in_natural_order():
            rep = '%s axis, size: %i' % (ax._get_name(), ax.size)
            p = self.lst_nav if ax.navigate else self.lst_sig
            i = QtWidgets.QListWidgetItem(rep)
            i.setData(QtCore.Qt.UserRole, ax)
            p.addItem(i)

        self._updating = False
        self.lst_nav.setUpdatesEnabled(True)
        self.lst_sig.setUpdatesEnabled(True)
        self._resize_controls()

    def _resize_controls(self):
        self.lst_nav.setUpdatesEnabled(False)
        self.lst_sig.setUpdatesEnabled(False)
        max_nav = max(self.lst_nav.sizeHint().height(), 20)
        max_sig = max(self.lst_sig.sizeHint().height(), 20)
        self.lst_nav.setFixedHeight(max_nav)
        self.lst_sig.setFixedHeight(max_sig)
        self.setFixedHeight(max_nav + max_sig + 150)
        self.lst_nav.setUpdatesEnabled(True)
        self.lst_sig.setUpdatesEnabled(True)

    def _move_item(self, item):
        ax = item.data(QtCore.Qt.UserRole)
        ax.navigate = not ax.navigate
        self.ui.record_code((
            "ax = ui.get_selected_signal().axes_manager[%s]\n"
            "ax.navigate = not ax.navigate\n"
            "ui.get_selected_wrapper().replot()") % (ax.index_in_array + 3j))
        self.signal.replot()

    def _list_move(self, item, dst_row, dst):
        """Called when drag and drop moved interal in list.
        """
        if self._updating:
            return
        ax = item.data(QtCore.Qt.UserRole)
        space = 1j if ax.navigate else 2j
        new_idx = dst_row + space
        self.plugin.rollaxis(ax, new_idx)

    def _list_insert(self, src_row, dst_row, dst):
        """Called when drag and drop moved between lists.
        """
        if self._updating:
            return
        # Switch space
        am = self.signal.signal.axes_manager
        old_space = 1j if dst is self.lst_sig else 2j
        old_idx = src_row + old_space
        ax = am[old_idx]
        dst.item(dst_row).setData(QtCore.Qt.UserRole, ax)
        ax.navigate = not ax.navigate
        self.ui.record_code((
            "ax = ui.get_selected_signal().axes_manager[%s]\n"
            "ax.navigate = not ax.navigate\n") % (ax.index_in_array + 3j))
        space = 1j if ax.navigate else 2j
        new_idx = dst_row + space
        self.plugin.rollaxis(ax, new_idx)

    def _move_down(self):
        if self.lst_nav.count() == 0:
            # nothing to transfer...
            return

        i = self.lst_nav.takeItem(self.lst_nav.currentRow())
        self.lst_sig.addItem(i)
        self._move_item(i)

    def _move_up(self):
        if self.lst_sig.count() == 0:
            # nothing to transfer...
            return
        # TODO: Track "active" list (only select in last?), and move int/ext as
        # needed
        i = self.lst_sig.takeItem(self.lst_sig.currentRow())
        self.lst_nav.addItem(i)
        self._move_item(i)

    def _flip_clicked(self):
        # Get selected axes
        axes = []
        for lst in (self.lst_nav, self.lst_sig):
            items = lst.selectedItems()
            axes.extend([i.data(QtCore.Qt.UserRole) for i in items])
        self.plugin.flip_axes(axes)

    def create_controls(self):
        self.lbl_nav = QLabel(tr("Navigate"), self)
        self.lst_nav = AxesListWidget(self)
        self.btn_up = QToolButton(self)
        self.btn_up.setArrowType(QtCore.Qt.UpArrow)
        self.btn_down = QToolButton(self)
        self.btn_down.setArrowType(QtCore.Qt.DownArrow)
        self.lbl_sig = QLabel(tr("Signal"), self)
        self.lst_sig = AxesListWidget(self)

        sp = self.lst_sig.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
        self.lst_sig.setSizePolicy(sp)
        sp = self.lst_nav.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Fixed)
        self.lst_nav.setSizePolicy(sp)

        self.btn_down.clicked.connect(self._move_down)
        self.btn_up.clicked.connect(self._move_up)
        self.lst_nav.inserted.connect(self._list_insert)
        self.lst_sig.inserted.connect(self._list_insert)
        self.lst_nav.moved.connect(self._list_move)
        self.lst_sig.moved.connect(self._list_move)

        self.btn_flip = QPushButton(tr("Reverse axes"))
        self.btn_flip.clicked.connect(self._flip_clicked)

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_nav)
        vbox.addWidget(self.lst_nav)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_up)
        hbox.addWidget(self.btn_down)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl_sig)
        vbox.addWidget(self.lst_sig)
        vbox.addWidget(self.btn_flip)

        w = QWidget()
        w.setLayout(vbox)
        self.setWidget(w)


class AxesListWidget(QtWidgets.QListWidget):
    inserted = QtCore.Signal(int, int, QtWidgets.QListWidget)
    moved = QtCore.Signal(QtWidgets.QListWidgetItem, int, QtWidgets.QListWidget)

    last_drop = None

    def __init__(self, type, parent=None):
        super().__init__(parent)
        self.setIconSize(QtCore.QSize(124, 124))
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        m = self.model()
        m.rowsInserted.connect(self._on_rows_inserted)
        m.rowsMoved.connect(self._on_rows_moved)

    def minimumSizeHint(self):
        s = QtCore.QSize()
        shfr = self.sizeHintForRow(0)
        if shfr < 0:
            shfr = 12
        h = shfr * self.count() + 2 * self.frameWidth()
        s.setHeight(h)
        s.setWidth(super().minimumSizeHint().width())
        return s

    def sizeHint(self):
        s = self.minimumSizeHint()
        s.setWidth(super().sizeHint().width())
        return s

    def _on_rows_inserted(self, parent, begin, end):
        for new_idx in range(begin, end+1):
            if AxesListWidget.last_drop:
                old_idx = AxesListWidget.last_drop.pop(0)
                self.inserted.emit(old_idx, new_idx, self)

    def _on_rows_moved(self, sourceParent, sourceStart, sourceEnd,
                       destinationParent, destinationRow):
        N = sourceEnd - sourceStart + 1
        for i in range(N):
            idx = destinationRow + i
            if destinationRow > sourceStart:
                idx -= N
            item = self.item(idx)
            self.moved.emit(item, idx, self)

    def decodeMimeData(self, data):
        result = {}
        stream = QtCore.QDataStream(data)
        while not stream.atEnd():
            row = stream.readInt32()
            stream.readInt32()                      # Column; not used
            item = result.setdefault(row, {})
            for role in range(stream.readInt32()):
                key = QtCore.Qt.ItemDataRole(stream.readInt32())
                item[key] = stream.readQVariant()
        return result

    def dropEvent(self, event):
        event.setDropAction(QtCore.Qt.MoveAction)
        m = event.mimeData()
        if m.hasFormat("application/x-qabstractitemmodeldatalist"):
            data = m.data("application/x-qabstractitemmodeldatalist")
            r = self.decodeMimeData(data)
            AxesListWidget.last_drop = []
            for k in r.keys():
                AxesListWidget.last_drop.append(k)
        super().dropEvent(event)
