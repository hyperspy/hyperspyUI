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
Created on Wed Jan 20 22:32:58 2016

@author: Vidar Tonaas Fauske
"""

import numpy as np
import matplotlib.pyplot as plt

from hyperspyui.plugins.plugin import Plugin
from hyperspyui.widgets.extendedqwidgets import FigureWidget
from hyperspyui.util import win2fig, fig2image_plot

from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtCore import Qt


def tr(text):
    return QtCore.QCoreApplication.translate("ColorMapPickerPlugi", text)


class CMapPickerPlugin(Plugin):
    name = "Color map picker"

    def create_widgets(self):
        w = CMapPickerWidget(self.ui, self.ui)
        w.plugin = self
        self.add_widget(w)
        # w.hide()  # Initial state hidden

    def change_cmap(self, cmap, mpl_axes=None):
        pass


# Have colormaps separated into categories:
# http://matplotlib.org/examples/color/colormaps_reference.html
cmaps = [('Uniform',        ['viridis', 'inferno', 'plasma', 'magma']),
         ('Sequential',     ['Blues', 'BuGn', 'BuPu',
                             'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                             'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                             'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']),
         ('Sequential (2)', ['afmhot', 'autumn', 'bone', 'cool',
                             'copper', 'gist_heat', 'gray', 'hot',
                             'pink', 'spring', 'summer', 'winter']),
         ('Diverging',      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                             'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                             'seismic']),
         ('Qualitative',    ['Accent', 'Dark2', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3']),
         ('Miscellaneous',  ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                             'brg', 'CMRmap', 'cubehelix',
                             'gnuplot', 'gnuplot2', 'gist_ncar',
                             'nipy_spectral', 'jet', 'rainbow',
                             'gist_rainbow', 'hsv', 'flag', 'prism'])]


class CMapDelegate(QtWidgets.QItemDelegate):
    """
    Delegate responsible for drawing a the entries in the colormap combobox.

    In addition to drawing a preview of the colormap, it also allows for
    parent elements to be added (group headings). The colormaps will be
    prepended by a set amount to prevent overlapping with the text.
    """

    def __init__(self, width, height, cmap_shift, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width_ = width
        self.height_ = height
        self.cmap_shift = cmap_shift

    @staticmethod
    def _create_pixmap(line, height):
        width = line.shape[0]
        data = line[:, [2, 1, 0, 3]]
        data = np.tile(data, (height, 1, 1))
        im = QtGui.QImage(data.data, width, height, QtGui.QImage.Format_ARGB32)
        im.ndarray = data
        return QtGui.QPixmap.fromImage(im)

    def paint(self, painter, option, index):

        kind = index.data(Qt.AccessibleDescriptionRole)
        if kind == "parent":
            option.state |= QtWidgets.QStyle.State_Enabled
            super().paint(painter, option, index)
        else:
            option.textElideMode = Qt.ElideNone
            rect = option.rect
            rect = QtCore.QRect(rect.x()+self.cmap_shift, rect.y(),
                                rect.width()-self.cmap_shift, rect.height())
            option.rect.setLeft(option.rect.x() + 10)
            super().paint(painter, option, index)

            cmap = plt.get_cmap(index.data().strip())
            width = self.width_ - self.cmap_shift
            line = cmap(np.linspace(0, 1, width, endpoint=True))
            line = (255 * line).astype(np.uint8)
            pixmap = self._create_pixmap(line, self.height_)
            painter.drawPixmap(rect, pixmap)

    def sizeHint(self, option, index):
        return QtCore.QSize(self.width_, self.height_)

    def drawFocus(self, painter, option, rect):
        super().drawFocus(painter, option, rect)


class CMapPickerWidget(FigureWidget):

    def __init__(self, main_window, parent, figure=None):
        super().__init__(main_window, parent)
        self.setWindowTitle(tr("Colormap Picker"))
        self.create_controls()

        self._on_figure_change(figure)

    def _on_select(self, cmap):
        img = self._cur_img
        if img is not None:
            for im in img:
                im.set_cmap(cmap)
            im.figure.canvas.draw()

    def _on_figure_change(self, figure):
        super()._on_figure_change(figure)
        if isinstance(figure, QtWidgets.QMdiSubWindow):
            figure = win2fig(figure)

        signals = self.parent().signals
        p = fig2image_plot(figure, signals)
        img = None
        if p is not None and len(p.ax.images) > 0:
            img = p.ax.images

        self._cur_img = img
        self.update_controls_from_fig()

    def update_controls_from_fig(self):
        img = self._cur_img
        if img is None:
            self.disable()
        else:
            self.enable()
            cmap = img[0].get_cmap().name
            self.cbo.setCurrentIndex(self.cbo.findText(cmap))

    def enable(self, enabled=True):
        self.cbo.setEnabled(enabled)

    def disable(self):
        self.enable(False)

    @staticmethod
    def make_parent_item(text):
        item = QtGui.QStandardItem(text)
        item.setFlags(item.flags() & ~(Qt.ItemIsEnabled | Qt.ItemIsSelectable))
        item.setData("parent", Qt.AccessibleDescriptionRole)

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        return item

    def create_controls(self):
        self.cbo = QtWidgets.QComboBox()
        self.cbo.setItemDelegate(CMapDelegate(256, 18, 80, self.cbo))
        for group, maps in cmaps:
            self.cbo.model().appendRow(self.make_parent_item(group))
            for cm in maps:
                self.cbo.addItem(cm)
        self.cbo.currentIndexChanged[str].connect(
            self._on_select)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.cbo)

        wrap = QtWidgets.QWidget()
        wrap.setLayout(vbox)
        height = vbox.sizeHint().height()
        wrap.setFixedHeight(height)
        self.setWidget(wrap)
