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
Created on Wed Jan 07 23:37:51 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from qtpy import QtCore, QtWidgets

from hyperspyui.widgets.extendedqwidgets import ExToolWindow


def tr(text):
    return QtCore.QCoreApplication.translate("Rebin", text)


class RebinPlugin(Plugin):
    name = "Rebin"

    def create_actions(self):
        self.add_action('rebin', tr("Rebin"), self.rebin_dialog,
                        icon='rebin.svg',
                        selection_callback=self.ui.select_signal,
                        tip=tr("Rebin the signal"))

    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions['rebin'])

    def rebin(self, factors, signal=None):
        if signal is None:
            signal = self.ui.get_selected_wrapper()
        s = signal.signal
        shape = []
        mods = [tuple()] * len(s.axes_manager.shape)
        for i in range(len(s.axes_manager.shape)):
            ax = s.axes_manager[i]
            factor = factors[i]
            if factor > ax.size:
                factor = ax.size
            if ax.size % factor == 0:
                mods[ax.index_in_array] = slice(None)
            else:
                mods[ax.index_in_array] = slice(None, - (ax.size % factor))
            shape.append(ax.size // factor)
        # Crop to multiple of factors
        s.data = s.data[tuple(mods)]

        # Update shape
        s.get_dimensions_from_data()

        # Do actual rebin
        signal.switch_signal(s.rebin(shape))
        self.ui.setUpdatesEnabled(False)
        try:
            signal.replot()
        finally:
            self.ui.setUpdatesEnabled(True)    # Always resume updates!
        self.record_code("<p>.rebin({0})".format(factors))

    def rebin_dialog(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_wrapper()
            if signal is None:
                return
        d = RebinDialog(signal, self, self.ui, self.ui)
        d.show()


class RebinDialog(ExToolWindow):

    def __init__(self, signal, plugin, ui, parent):
        super().__init__(parent)
        self.signal = signal
        self.ui = ui
        self.setWindowTitle(tr("Rebin ") + signal.name)
        self.create_controls()
        self.plugin = plugin

    def rebin(self):
        factors = []
        for ax in self.signal.signal.axes_manager._get_axes_in_natural_order():
            spin = self.spins[ax.name]
            factors.append(spin.value())
        self.plugin.rebin(factors, self.signal)

    def validate(self):
        style = QtWidgets.QApplication.style()
        tmpIcon = style.standardIcon(style.SP_MessageBoxWarning, None, self)
        s = self.signal
        for ax in s.signal.axes_manager._get_axes_in_natural_order():
            spin = self.spins[ax.name]
            hbox = self.hboxes[ax.name]
            if ax.size % spin.value() != 0:
                # Not a factor, show warning
                if hbox.count() <= 1:
                    # No warning icon yet
                    iconSize = spin.height()
                    pm = tmpIcon.pixmap(iconSize, iconSize)
                    lbl = QtWidgets.QLabel()
                    lbl.setPixmap(pm)
                    lbl.setToolTip(tr("Not a factor of shape. Input data " +
                                      "will be trimmed before binning."))
                    sp = lbl.sizePolicy()
                    sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Maximum)
                    lbl.setSizePolicy(sp)
                    hbox.insertWidget(0, lbl)
            else:
                # Everything OK, remove warning icon if there
                if hbox.count() > 1:
                    lbl = hbox.takeAt(0)
                    lbl.widget().deleteLater()

    def create_controls(self):
        self.spins = {}
        self.hboxes = {}
        form = QtWidgets.QFormLayout()
        for ax in self.signal.signal.axes_manager._get_axes_in_natural_order():
            spin = QtWidgets.QSpinBox(self)
            spin.setValue(1)
            spin.setMinimum(1)
            spin.valueChanged.connect(self.validate)
            self.spins[ax.name] = spin
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(spin)
            form.addRow(ax.name, hbox)
            self.hboxes[ax.name] = hbox
        self.form = form
        self.btn_rebin = QtWidgets.QPushButton(tr("Rebin"))
        self.btn_rebin.clicked.connect(self.rebin)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.btn_rebin)

        self.setLayout(vbox)
