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
Created on Sun Mar 01 15:18:30 2015

@author: Vidar Tonaas Fauske
"""

from hyperspyui.plugins.plugin import Plugin

from qtpy import QtCore
from qtpy.QtWidgets import QMessageBox

import hyperspy.utils.plot


def tr(text):
    return QtCore.QCoreApplication.translate("MirrorPlotPlugin", text)


class MirrorPlotPlugin(Plugin):
    name = "Mirror plot"

    def create_actions(self):
        self.add_action('mirror', "Mirror navigation", self.mirror_navi,
                        icon='mirror.svg',
                        selection_callback=self.ui.select_signal,
                        tip="Mirror navigation axes of selected signals")
        self.add_action('share_nav', "Share navigation", self.share_navi,
                        icon='intersection.svg',
                        selection_callback=self.ui.select_signal,
                        tip="Mirror navigation axes of selected signals")

    def create_menu(self):
        self.add_menuitem('Signal', self.ui.actions['mirror'])
        self.add_menuitem('Signal', self.ui.actions['share_nav'])

    def create_toolbars(self):
        self.add_toolbar_button("Signal", self.ui.actions['mirror'])
        self.add_toolbar_button("Signal", self.ui.actions['share_nav'])

    def share_navi(self, uisignals=None):
        self.mirror_navi(uisignals, shared_nav=True)

    def mirror_navi(self, uisignals=None, shared_nav=False):
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
            if shared_nav:
                navs = ["auto"]
                navs.extend([None] * (len(signals)-1))
                hyperspy.utils.plot.plot_signals(signals, sync=True,
                                                 navigator_list=navs)
            else:
                hyperspy.utils.plot.plot_signals(signals, sync=True)
        finally:
            self.ui.setUpdatesEnabled(True)    # Continue updating UI
