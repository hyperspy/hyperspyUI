# -*- coding: utf-8 -*-
"""
Created on Sun Mar 01 15:18:30 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

import hyperspy.utils.plot


def tr(text):
    return QCoreApplication.translate("MirrorPlotPlugin", text)


class MirrorPlotPlugin(Plugin):
    name = "Mirror plot"

    def create_actions(self):
        self.add_action('mirror', "Mirror", self.mirror_navi,
                        icon='mirror.svg',
                        selection_callback=self.ui.select_signal,
                        tip="Mirror navigation axes of selected signals")

    def create_menus(self):
        self.add_menuitem('Signal', self.ui.actions['mirror'])

    def create_toolbars(self):
        self.add_toolbar_button("Signal", self.ui.actions['mirror'])

    def mirror_navi(self, uisignals=None):
        # Select signals
        if uisignals is None:
            uisignals = self.ui.get_selected_wrappers()
        if len(uisignals) < 2:
            mb = QMessageBox(QMessageBox.Information, tr("Select two or more"),
                             tr("You need to select two or more signals" +
                                " to mirror"), QMessageBox.Ok)
            mb.exec_()
            return

        signals = [s.signal for s in uisignals]

        # hyperspy closes, and then recreates figures when mirroring
        # the navigators. To keep UI from flickering, we suspend updates.
        # SignalWrapper also saves and then restores window geometry
        self.ui.setUpdatesEnabled(False)
        try:
            hyperspy.utils.plot.plot_signals(signals)
        finally:
            self.ui.setUpdatesEnabled(True)    # Continue updating UI
