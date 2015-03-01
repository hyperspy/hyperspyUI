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


class RebinDialog(ExToolWindow):

    def __init__(self, signal, ui, parent):
        super(RebinDialog, self).__init__(parent)
        self.signal = signal
        self.ui = ui
        self.setWindowTitle(tr("Rebin ") + signal.name)
        self.create_controls()

    def rebin(self):
        shape = []
        s = self.signal
        for ax in s.signal.axes_manager._get_axes_in_natural_order():
            spin = self.spins[ax.name]
            factor = spin.value()
            shape.append(ax.size / factor)

        try:
            s.signal = s.signal.rebin(shape)
        except ValueError:
            mb = QMessageBox(QMessageBox.Critical, tr("Invalid rebin factor"),
                             tr("Can only rebin by factors of the original " +
                                "dimensions (e.g. 4 can be rebinned by 1, 2 or " +
                                "4, but not 3)."),
                             QMessageBox.Ok)
            mb.exec_()
            return
        self.ui.setUpdatesEnabled(False)
        try:
            s.replot()
        finally:
            self.ui.setUpdatesEnabled(True)    # Always resume updates!

    def create_controls(self):
        self.spins = {}
        form = QFormLayout()
        for ax in self.signal.signal.axes_manager._get_axes_in_natural_order():
            spin = QSpinBox(self)
            spin.setValue(1)
            spin.setMinimum(1)
            self.spins[ax.name] = spin
            form.addRow(ax.name, spin)

        self.btn_rebin = QPushButton(tr("Rebin"))
        self.btn_rebin.clicked.connect(self.rebin)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.btn_rebin)

        self.setLayout(vbox)


class RebinPlugin(Plugin):
    name = "Rebin"

    def create_actions(self):
        self.add_action('rebin', tr("Rebin"), self.rebin_dialog,
                        #                        icon='rebin.svg',
                        selection_callback=self.ui.select_signal,
                        tip=tr("Rebin the signal"))

    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions['rebin'])

    def rebin_dialog(self, signal=None):
        if signal is None:
            signal = self.ui.get_selected_signal()
            if signal is None:
                return
        d = RebinDialog(signal, self.ui, self.ui)
        d.show()
