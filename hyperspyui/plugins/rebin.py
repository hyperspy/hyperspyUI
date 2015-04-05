# -*- coding: utf-8 -*-
"""
Created on Wed Jan 07 23:37:51 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.widgets.extendedqwidgets import ExToolWindow


def tr(text):
    return QCoreApplication.translate("Rebin", text)


class RebinPlugin(Plugin):
    name = "Rebin"

    def create_actions(self):
        self.add_action('rebin', tr("Rebin"), self.rebin_dialog,
                        #                        icon='rebin.svg',
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
        for i in xrange(len(s.axes_manager.shape)):
            ax = s.axes_manager[i]
            factor = factors[i]
            if factor > ax.size:
                factor = ax.size
            if ax.size % factor == 0:
                mods[ax.index_in_array] = slice(None)
            else:
                mods[ax.index_in_array] = slice(None, - (ax.size % factor))
            shape.append(ax.size / factor)
        # Crop to multiple of factors
        s.data = s.data[tuple(mods)]

        # Update shape, but prevent auto_replot
        old = s.auto_replot
        s.auto_replot = False
        s.get_dimensions_from_data()
        s.auto_replot = old

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
        super(RebinDialog, self).__init__(parent)
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
        style = QApplication.style()
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
                    lbl = QLabel()
                    lbl.setPixmap(pm)
                    lbl.setToolTip(tr("Not a factor of shape. Input data " +
                                      "will be trimmed before binning."))
                    sp = lbl.sizePolicy()
                    sp.setHorizontalPolicy(QSizePolicy.Maximum)
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
        form = QFormLayout()
        for ax in self.signal.signal.axes_manager._get_axes_in_natural_order():
            spin = QSpinBox(self)
            spin.setValue(1)
            spin.setMinimum(1)
            spin.valueChanged.connect(self.validate)
            self.spins[ax.name] = spin
            hbox = QHBoxLayout()
            hbox.addWidget(spin)
            form.addRow(ax.name, hbox)
            self.hboxes[ax.name] = hbox
        self.form = form
        self.btn_rebin = QPushButton(tr("Rebin"))
        self.btn_rebin.clicked.connect(self.rebin)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.btn_rebin)

        self.setLayout(vbox)
