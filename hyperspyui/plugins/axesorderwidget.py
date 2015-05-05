# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:00:55 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore

from hyperspyui.util import win2sig
from hyperspyui.widgets.extendedqwidgets import FigureWidget


def tr(text):
    return QtCore.QCoreApplication.translate("AxesOrderPlugin", text)


class AxesOrderPlugin(Plugin):
    name = "Axes order widget"

    def create_widgets(self):
        w = AxesOrderWidget(self.ui, self.ui)
        self.add_widget(w)
        w.hide()  # Initial state hidden


class AxesOrderWidget(FigureWidget):

    def __init__(self, ui, parent=None):
        super(AxesOrderWidget, self).__init__(ui, parent)
        self.setWindowTitle(tr("Axes order"))
        self.signal = None
        self.create_controls()
        self._resize_controls()

    def _on_figure_change(self, win):
        super(AxesOrderWidget, self)._on_figure_change(win)
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
            rep = rep.encode('utf8')
            p = self.lst_nav if ax.navigate else self.lst_sig
            i = QtGui.QListWidgetItem(rep)
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
        self.setFixedHeight(max_nav + max_sig + 110)
        self.lst_nav.setUpdatesEnabled(True)
        self.lst_sig.setUpdatesEnabled(True)

    def _move_item(self, item):
        ax = item.data(QtCore.Qt.UserRole)
        ax.navigate = not ax.navigate
        self.signal.replot()

    def _list_move(self, item, dst_row, dst):
        """Called when drag and drop moved interal in list.
        """
        if self._updating:
            return
        ax = item.data(QtCore.Qt.UserRole)
        # Reorder
        am = self.signal.signal.axes_manager
        space = 1j if ax.navigate else 2j
        old_idx = am._axes.index(ax) + 3j
        new_idx = dst_row + space
        new_s = self.signal.signal.rollaxis(old_idx, new_idx)
        self.signal.switch_signal(new_s)
        self.signal.replot()

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
        old_idx = am._axes.index(ax) + 3j
        ax.navigate = not ax.navigate
        space = 1j if ax.navigate else 2j
        new_idx = dst_row + space
        new_s = self.signal.signal.rollaxis(old_idx, new_idx)
        self.signal.switch_signal(new_s)
        self.signal.replot()

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

    def create_controls(self):
        self.lbl_nav = QtGui.QLabel(tr("Navigate"), self)
        self.lst_nav = AxesListWidget(self)
        self.btn_up = QtGui.QToolButton(self)
        self.btn_up.setArrowType(QtCore.Qt.UpArrow)
        self.btn_down = QtGui.QToolButton(self)
        self.btn_down.setArrowType(QtCore.Qt.DownArrow)
        self.lbl_sig = QtGui.QLabel(tr("Signal"), self)
        self.lst_sig = AxesListWidget(self)

        sp = self.lst_sig.sizePolicy()
        sp.setVerticalPolicy(QtGui.QSizePolicy.Fixed)
        self.lst_sig.setSizePolicy(sp)
        sp = self.lst_nav.sizePolicy()
        sp.setVerticalPolicy(QtGui.QSizePolicy.Fixed)
        self.lst_nav.setSizePolicy(sp)

        self.btn_down.clicked.connect(self._move_down)
        self.btn_up.clicked.connect(self._move_up)
        self.lst_nav.inserted.connect(self._list_insert)
        self.lst_sig.inserted.connect(self._list_insert)
        self.lst_nav.moved.connect(self._list_move)
        self.lst_sig.moved.connect(self._list_move)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.lbl_nav)
        vbox.addWidget(self.lst_nav)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_up)
        hbox.addWidget(self.btn_down)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl_sig)
        vbox.addWidget(self.lst_sig)

        w = QtGui.QWidget()
        w.setLayout(vbox)
        self.setWidget(w)


class AxesListWidget(QtGui.QListWidget):
    inserted = QtCore.Signal(int, int, QtGui.QListWidget)
    moved = QtCore.Signal(QtGui.QListWidgetItem, int, QtGui.QListWidget)

    last_drop = None

    def __init__(self, type, parent=None):
        super(AxesListWidget, self).__init__(parent)
        self.setIconSize(QtCore.QSize(124, 124))
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
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
        s.setWidth(super(AxesListWidget, self).sizeHint().width())
        return s

    def sizeHint(self):
        return self.minimumSizeHint()

    def _on_rows_inserted(self, parent, begin, end):
        for new_idx in xrange(begin, end+1):
            if AxesListWidget.last_drop:
                old_idx = AxesListWidget.last_drop.pop(0)
                self.inserted.emit(old_idx, new_idx, self)

    def _on_rows_moved(self, sourceParent, sourceStart, sourceEnd,
                       destinationParent, destinationRow):
        N = sourceEnd - sourceStart + 1
        for i in xrange(N):
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
            for k in r.iterkeys():
                AxesListWidget.last_drop.append(k)
        super(AxesListWidget, self).dropEvent(event)
