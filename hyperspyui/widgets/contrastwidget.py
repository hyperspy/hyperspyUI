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
Created on Wed Oct 29 16:49:48 2014

@author: Vidar Tonaas Fauske
"""


from qtpy import QtCore, QtWidgets

from .extendedqwidgets import FigureWidget, ExDoubleSlider, ExClickLabel
from hyperspy.misc.rgb_tools import rgbx2regular_array
from hyperspyui.util import win2fig, fig2image_plot, block_signals

import numpy as np
from matplotlib.colors import Normalize, SymLogNorm


def tr(text):
    return QtCore.QCoreApplication.translate("ContrastWidget", text)


def _auto_contrast(plot):
    return [plot._vmin_user is None, plot._vmax_user is None]


def _set_auto_contrast(plot, auto):
    if auto:
        plot._vmin_user = None
        plot._vmax_user = None
    else:
        plot._vmin_user = plot.vmin
        plot._vmax_user = plot.vmax


class ContrastWidget(FigureWidget):
    LevelLabel = tr("Level")
    WindowLabel = tr("Window")

    def __init__(self, main_window, parent, figure=None):
        super(ContrastWidget, self).__init__(main_window, parent)
        self.setWindowTitle(tr("Contrast control"))
        self.create_controls()

        self._on_figure_change(figure)

    def _on_figure_change(self, figure):
        super(ContrastWidget, self)._on_figure_change(figure)
        if isinstance(figure, QtWidgets.QMdiSubWindow):
            figure = win2fig(figure)

        signals = self.parent().signals
        p = fig2image_plot(figure, signals)
        self._cur_plot = p
        self.update_controls_from_fig()

    def _plot_minmax(self):
        p = self._cur_plot
        if p is None:
            return 0.0, 0.0
        data = rgbx2regular_array(p.data_function().ravel())
        return np.nanmin(data), np.nanmax(data)

    def update_controls_from_fig(self):
        p = self._cur_plot
        if p is None:
            self.sl_level.setValue(0.0)
            self.sl_window.setValue(0.0)
            self.chk_log.setChecked(False)
            self.disable()
        else:
            self.enable()
            imin, imax = self._plot_minmax()

            with block_signals(self.sl_level):
                self.sl_level.setRange(imin, imax)
                self.sl_level.setValue(p.vmin)
                self.lbl_level.setText(self.LevelLabel + ": %.2G" % p.vmin)

            with block_signals(self.sl_window):
                self.sl_window.setRange(0, imax - imin)
                window = p.vmax - p.vmin
                self.sl_window.setValue(window)
                self.lbl_window.setText(self.WindowLabel + ": %.2G" % window)

            with block_signals(self.chk_auto):
                auto = _auto_contrast(p)
                state = QtCore.Qt.Checked if all(auto) else (
                    QtCore.Qt.PartiallyChecked if any(auto) else
                    QtCore.Qt.Unchecked)
                self.chk_auto.setCheckState(state)

            if p.ax.images:
                with block_signals(self.chk_log):
                    self.chk_log.setEnabled(True)
                    norm = isinstance(p.ax.images[-1].norm, SymLogNorm)
                    self.chk_log.setChecked(norm)
            else:
                self.chk_log.setEnabled(False)

    def level_changed(self, value):
        self.lbl_level.setText(self.LevelLabel + ": %.2G" % value)
        p = self._cur_plot
        if p is not None:
            p.vmin = self.sl_level.value()
            p.vmax = self.sl_level.value() + self.sl_window.value()
            if self.chk_auto.isChecked():
                self.chk_auto.setChecked(False)
            p.update()

    def window_changed(self, value):
        self.lbl_window.setText(self.WindowLabel + ": %.2G" % value)
        p = self._cur_plot
        if p is not None:
            p.vmax = self.sl_level.value() + self.sl_window.value()
            if self.chk_auto.isChecked():
                self.chk_auto.setChecked(False)
            p.update()

    def log_changed(self, value):
        p = self._cur_plot
        if p is not None and p.ax.images:
            old = p.ax.images[0].norm
            kw = dict(vmin=old.vmin, vmax=old.vmax, clip=old.clip)
            if value:
                n = SymLogNorm(1e-9, **kw)
            else:
                n = Normalize(**kw)
            p.ax.images[-1].norm = n
            p.update()

    def enable(self, enabled=True):
        self.lbl_level.setEnabled(enabled)
        self.lbl_window.setEnabled(enabled)
        self.sl_level.setEnabled(enabled)
        self.sl_window.setEnabled(enabled)
        self.chk_auto.setEnabled(enabled)
        self.chk_log.setEnabled(enabled)

    def disable(self):
        self.enable(False)

    def auto(self, state):
        p = self._cur_plot
        if p is not None:
            _set_auto_contrast(p, state == QtCore.Qt.Checked)
            p.update()
            self.update_controls_from_fig()

    def reset_level(self):
        imin, imax = self._plot_minmax()
        self.sl_level.setValue(imin)   # Will trigger events

    def reset_window(self):
        imin, imax = self._plot_minmax()
        self.sl_window.setValue(imax - imin)   # Will trigger events

    def create_controls(self):
        self.sl_level = ExDoubleSlider(self, QtCore.Qt.Horizontal)
        self.lbl_level = ExClickLabel(self.LevelLabel + ": 0.0")
        self.sl_window = ExDoubleSlider(self, QtCore.Qt.Horizontal)
        self.lbl_window = ExClickLabel(self.WindowLabel + ": 0.0")

        for sl in [self.sl_level, self.sl_window]:
            sl.setRange(0.0, 1.0)
            sl.setValue(0.0)

        self.chk_auto = QtWidgets.QCheckBox(tr("Auto"), self)
        self.chk_log = QtWidgets.QCheckBox(tr("Log"), self)

        # Test level/window working?
        self.lbl_level.clicked.connect(self.reset_level)
        self.lbl_window.clicked.connect(self.reset_window)
        self.sl_level.valueChanged[float].connect(self.level_changed)
        self.sl_window.valueChanged[float].connect(self.window_changed)
        self.chk_auto.stateChanged[int].connect(self.auto)
        self.chk_log.toggled[bool].connect(self.log_changed)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.chk_auto)
        hbox.addWidget(self.chk_log)
        vbox = QtWidgets.QVBoxLayout()
        for w in [self.sl_level, self.lbl_level,
                  self.sl_window, self.lbl_window]:
            vbox.addWidget(w)
        vbox.addLayout(hbox)

        wrap = QtWidgets.QWidget()
        wrap.setLayout(vbox)
        height = vbox.sizeHint().height()
        wrap.setFixedHeight(height)
        self.setWidget(wrap)
